# 🐑 بوت أضاحي تيليغرام

بوت يراقب موقع adhahi.dz ويرسل إشعاراً فور توفر أضاحي في أي ولاية.

---

## 🚀 طريقة النشر على Railway.app (مجاني)

### الخطوة 1: إنشاء بوت تيليغرام

1. افتح تيليغرام وابحث عن **@BotFather**
2. أرسل `/newbot`
3. اختر اسماً للبوت
4. احفظ الـ **Token** الذي يعطيك إياه

### الخطوة 2: الحصول على Chat ID

1. ابحث عن **@userinfobot** في تيليغرام
2. أرسل له `/start`
3. سيعطيك الـ **Chat ID** الخاص بك

### الخطوة 3: رفع الكود على GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/adhahi-bot.git
git push -u origin main
```

### الخطوة 4: النشر على Railway

1. اذهب إلى [railway.app](https://railway.app)
2. سجّل دخول بحساب GitHub
3. اضغط **New Project** → **Deploy from GitHub repo**
4. اختر مستودع `adhahi-bot`
5. اذهب إلى **Variables** وأضف:

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | التوكن من BotFather |
| `CHAT_ID` | الـ ID الخاص بك |
| `CHECK_INTERVAL` | `60` (كل 60 ثانية) |

6. اضغط **Deploy** ✅

---

## ⚙️ متغيرات البيئة

| المتغير | الوصف | مثال |
|---------|-------|-------|
| `BOT_TOKEN` | توكن البوت من BotFather | `123:ABCdef...` |
| `CHAT_ID` | معرّف محادثتك | `123456789` |
| `CHECK_INTERVAL` | الفترة بين كل فحص (ثانية) | `60` |

---

## 📱 ماذا يفعل البوت؟

- ✅ يفحص API الموقع كل دقيقة (أو حسب إعدادك)
- 🔔 يرسل إشعاراً فور ظهور ولاية متاحة جديدة
- 📈 يرسل إشعاراً إذا زادت الحصص في ولاية
- 🤖 يرسل رسالة تأكيد عند بدء التشغيل

---

## 🧪 تشغيل محلي (للاختبار)

```bash
pip install -r requirements.txt

# Linux/Mac
export BOT_TOKEN="your_token"
export CHAT_ID="your_chat_id"
python bot.py

# Windows
set BOT_TOKEN=your_token
set CHAT_ID=your_chat_id
python bot.py
```
