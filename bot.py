import requests
import re
import time
import logging
from datetime import datetime

# 🔧 تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gold_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 🔧 اطلاعات ربات
BOT_TOKEN = "7631678304:AAFrAGbsyNt8-2Y3gwtyqdgKfh2kAKDg3_E"
CHANNEL_ID = "@sekehprice"

# ثابت‌ها
ONS_TO_GRAM = 31.1035
GOLD_18_RATIO = 0.750
COIN_GOLD_WEIGHT_RATIO = 0.2354

class GoldPriceBot:
    def __init__(self):
        self.last_ons_price = 0
        self.last_usdt_price = 0
        self.last_coin_bubble_price = 0
        self.last_prices = {}
        self.error_count = 0
        self.max_errors = 10
        
    def robust_request(self, url, timeout=15, retries=3):
        """درخواست با قابلیت تلاش مجدد"""
        for attempt in range(retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    self.error_count = 0
                    return response
            except requests.exceptions.RequestException as e:
                logging.warning(f"خطای ارتباطی (تلاش {attempt + 1}/{retries}): {e}")
                time.sleep(2)
        
        self.error_count += 1
        return None
    
    def get_ons_price_from_channel(self):
        """دریافت قیمت انس طلا"""
        try:
            response = self.robust_request("https://t.me/s/ounceOnlineRate")
            if response:
                patterns = [
                    r'انس طلا.*?(\d{1,3}(?:,\d{3})*\.\d{2})',
                    r'(\d{1,3}(?:,\d{3})*\.\d{2}).*?دلار',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        latest_price = matches[-1]
                        price = float(latest_price.replace(',', ''))
                        return {'price': price, 'success': True}
            
            return {'success': False, 'error': 'قیمت انس طلا پیدا نشد'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_usdt_price_from_channel(self):
        """دریافت قیمت تتر"""
        try:
            response = self.robust_request("https://t.me/s/USDT_RLS")
            if response:
                patterns = [
                    r'(\d{1,3}(?:,\d{3})*)\s*تومان',
                    r'تتر.*?(\d{1,3}(?:,\d{3})*)',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        latest_price = matches[-1]
                        price = int(latest_price.replace(',', ''))
                        return {'price': price, 'success': True}
            
            return {'success': False, 'error': 'قیمت تتر پیدا نشد'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_coin_price_with_bubble(self):
        """دریافت قیمت سکه با حباب"""
        try:
            response = self.robust_request("https://t.me/s/sekkedollarrate")
            if response:
                patterns = [
                    r'سکه.*?(\d{3},\d{3})',
                    r'سکه.*?(\d{6})',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        latest_price = matches[-1]
                        base_price = int(latest_price.replace(',', ''))
                        price = base_price * 1000
                        return {
                            'price': price,
                            'success': True,
                            'original_price': latest_price
                        }
            
            return {'success': False, 'error': 'قیمت سکه با حباب پیدا نشد'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def calculate_gold_prices(self, ons_price_dollar, usdt_price_toman):
        """محاسبه قیمت‌های طلا"""
        try:
            gold_24_per_gram_dollar = ons_price_dollar / ONS_TO_GRAM
            gold_18_per_gram_dollar = gold_24_per_gram_dollar * GOLD_18_RATIO
            gold_24_per_gram_toman = gold_24_per_gram_dollar * usdt_price_toman
            gold_18_per_gram_toman = gold_18_per_gram_dollar * usdt_price_toman
            
            return {
                'gold_24_per_gram_toman': int(gold_24_per_gram_toman),
                'gold_18_per_gram_toman': int(gold_18_per_gram_toman),
                'success': True
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def calculate_coin_price(self, ons_price_dollar, usdt_price_toman):
        """محاسبه قیمت ذاتی سکه"""
        try:
            coin_intrinsic_price = ons_price_dollar * usdt_price_toman * COIN_GOLD_WEIGHT_RATIO
            return {'coin_intrinsic': int(coin_intrinsic_price), 'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_telegram_message(self, message):
        """ارسال پیام به تلگرام"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def run(self):
        """اجرای اصلی ربات"""
        counter = 0
        
        while True:
            try:
                counter += 1
                current_time = datetime.now().strftime('%H:%M:%S')
                
                if self.error_count > self.max_errors:
                    wait_time = 60
                    logging.warning(f"خطاهای زیاد! منتظر {wait_time} ثانیه...")
                    time.sleep(wait_time)
                    self.error_count = 0
                
                # دریافت قیمت‌ها
                ons_result = self.get_ons_price_from_channel()
                usdt_result = self.get_usdt_price_from_channel()
                coin_bubble_result = self.get_coin_price_with_bubble()
                
                send_message = False
                
                # بررسی تغییرات قیمت
                if ons_result['success']:
                    ons_price = ons_result['price']
                    if ons_price != self.last_ons_price or counter == 1:
                        send_message = True
                        self.last_ons_price = ons_price
                
                if usdt_result['success']:
                    usdt_price = usdt_result['price']
                    if usdt_price != self.last_usdt_price or counter == 1:
                        send_message = True
                        self.last_usdt_price = usdt_price
                
                if coin_bubble_result['success']:
                    coin_bubble_price = coin_bubble_result['price']
                    if coin_bubble_price != self.last_coin_bubble_price or counter == 1:
                        send_message = True
                        self.last_coin_bubble_price = coin_bubble_price
                
                # محاسبات
                if ons_result['success'] and usdt_result['success']:
                    gold_result = self.calculate_gold_prices(ons_price, usdt_price)
                    coin_result = self.calculate_coin_price(ons_price, usdt_price)
                    
                    current_prices = {**gold_result, **coin_result}
                    if current_prices != self.last_prices or counter == 1:
                        send_message = True
                        self.last_prices = current_prices
                
                # ارسال پیام
                if send_message and all([
                    ons_result['success'], usdt_result['success'], 
                    gold_result['success'], coin_result['success'],
                    coin_bubble_result['success']
                ]):
                    bubble_percentage = ((coin_bubble_price - coin_result['coin_intrinsic']) / coin_result['coin_intrinsic']) * 100
                    
                    message = f"""**انس جهانی طلا**
**💰 {ons_price:,.2f} دلار**

**تتر**
**💵 {usdt_price:,} تومان**

**طلای ۲۴ عیار (هر گرم)**
**🏷️ {gold_result['gold_24_per_gram_toman']:,} تومان**

**طلای ۱۸ عیار (هر گرم)**
**🏷️ {gold_result['gold_18_per_gram_toman']:,} تومان**

**سکه تمام (ذاتی)**
**🪙 {coin_result['coin_intrinsic']:,} تومان**

**سکه تمام (با حباب)**
**💎 {coin_bubble_price:,} تومان**

**حباب سکه**
**📊 {bubble_percentage:+.1f}%**

**⏰ {current_time}**

@sekehprice"""
                    
                    if self.send_telegram_message(message):
                        logging.info(f"✅ ارسال موفق - {current_time}")
                    else:
                        logging.error(f"❌ خطا در ارسال - {current_time}")
                
                else:
                    logging.info(f"⏸️ قیمت تغییر نکرده - {current_time}")
                
                time.sleep(10)
                
            except KeyboardInterrupt:
                logging.info("🛑 ربات متوقف شد")
                break
            except Exception as e:
                logging.error(f"❌ خطای غیرمنتظره: {e}")
                time.sleep(30)

if __name__ == "__main__":
    bot = GoldPriceBot()
    logging.info("🚀 ربات قیمت‌گذاری طلا شروع به کار کرد")

    bot.run()
