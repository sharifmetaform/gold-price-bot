import requests
import time
import re
from datetime import datetime

# 🔧 اطلاعات ربات
BOT_TOKEN = "7631678304:AAFrAGbsyNt8-2Y3gwtyqdgKfh2kAKDg3_E"
CHANNEL_ID = "@sekehprice"

def get_ons_price_from_channel():
    """دریافت قیمت انس طلا از کانال @ounceOnlineRate"""
    try:
        url = "https://t.me/s/ounceOnlineRate"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            patterns = [
                r'انس طلا.*?(\d{1,3}(?:,\d{3})*\.\d{2})',
                r'(\d{1,3}(?:,\d{3})*\.\d{2}).*?دلار',
                r'قیمت لحظه ای انس طلا.*?(\d{1,3}(?:,\d{3})*\.\d{2})'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    latest_price = matches[-1]
                    price = float(latest_price.replace(',', ''))
                    return {
                        'price': price,
                        'success': True
                    }
        
        return {'success': False, 'error': 'قیمت انس طلا پیدا نشد'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_silver_price_from_channel():
    """دریافت قیمت انس نقره از کانال @SilverPriceLive"""
    try:
        url = "https://t.me/s/SilverPriceLive"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            patterns = [
                r'نقره.*?(\d{1,3}(?:,\d{3})*\.\d{2})',
                r'(\d{1,3}(?:,\d{3})*\.\d{2}).*?دلار',
                r'سکه.*?(\d{1,3}(?:,\d{3})*\.\d{2})',
                r'قیمت.*?(\d{1,3}(?:,\d{3})*\.\d{2})'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    latest_price = matches[-1]
                    price = float(latest_price.replace(',', ''))
                    return {
                        'price': price,
                        'success': True
                    }
        
        return {'success': False, 'error': 'قیمت انس نقره پیدا نشد'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_usdt_price_from_channel():
    """دریافت قیمت تتر از کانال @USDT_RLS"""
    try:
        url = "https://t.me/s/USDT_RLS"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*تومان',
                r'تتر.*?(\d{1,3}(?:,\d{3})*)',
                r'USDT.*?(\d{1,3}(?:,\d{3})*)',
                r'قیمت.*?(\d{1,3}(?:,\d{3})*).*?تومان'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    latest_price = matches[-1]
                    price = int(latest_price.replace(',', ''))
                    return {
                        'price': price,
                        'success': True
                    }
        
        return {'success': False, 'error': 'قیمت تتر پیدا نشد'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def send_telegram_message(message):
    """ارسال پیام به تلگرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        return True
    except:
        return False

def main():
    print("💰 ربات قیمت لحظه‌ای انس طلا، نقره و تتر")
    print("📡 دریافت از @ounceOnlineRate, @SilverPriceLive و @USDT_RLS")
    print("⚡ هر 3 ثانیه آپدیت")
    print("🛑 متوقف کردن: Ctrl + C")
    
    counter = 0
    last_ons_price = 0
    last_silver_price = 0
    last_usdt_price = 0
    
    while True:
        counter += 1
        current_time = time.strftime("%H:%M:%S")
        
        # دریافت قیمت‌ها
        ons_result = get_ons_price_from_channel()
        silver_result = get_silver_price_from_channel()
        usdt_result = get_usdt_price_from_channel()
        
        # فقط اگر قیمت‌ها تغییر کردند یا اولین بار هست
        send_message = False
        
        if ons_result['success']:
            ons_price = ons_result['price']
            if ons_price != last_ons_price or counter == 1:
                send_message = True
                last_ons_price = ons_price
        
        if silver_result['success']:
            silver_price = silver_result['price']
            if silver_price != last_silver_price or counter == 1:
                send_message = True
                last_silver_price = silver_price
        
        if usdt_result['success']:
            usdt_price = usdt_result['price']
            if usdt_price != last_usdt_price or counter == 1:
                send_message = True
                last_usdt_price = usdt_price
        
        if send_message and ons_result['success'] and silver_result['success'] and usdt_result['success']:
            # ساخت پیام با سه عنوان
            message = f"""**انس جهانی طلا**
**💰 {ons_price:,.2f} دلار**

**انس جهانی نقره**
**⚪ {silver_price:,.2f} دلار**

**تتر**
**💵 {usdt_price:,} تومان**

**⏰ {current_time}**

@sekehprice"""
            
            # ارسال پیام
            if send_telegram_message(message):
                print(f"✅ طلا: ${ons_price:,.2f} | نقره: ${silver_price:,.2f} | تتر: {usdt_price:,} تومان - {current_time}")
            else:
                print(f"❌ خطا در ارسال")
        
        elif not ons_result['success']:
            print(f"❌ خطا در دریافت انس طلا: {ons_result['error']}")
        elif not silver_result['success']:
            print(f"❌ خطا در دریافت انس نقره: {silver_result['error']}")
        elif not usdt_result['success']:
            print(f"❌ خطا در دریافت تتر: {usdt_result['error']}")
        else:
            print(f"⏸️ قیمت تغییر نکرده - {current_time}")
        
        # انتظار 3 ثانیه
        time.sleep(3)

if __name__ == "__main__":
    main()