import asyncio
import aiohttp
import os
import logging
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN      = os.getenv("BOT_TOKEN")
CHAT_ID        = os.getenv("CHAT_ID")
CHANNEL_ID     = os.getenv("CHANNEL_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

API_URL = "https://adhahi.dz/api/v1/public/wilaya-quotas"

previous_available = {}


async def fetch_quotas(session):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Origin": "https://adhahi.dz",
            "Referer": "https://adhahi.dz/"
        }
        async with session.get(API_URL, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"API status: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return None


def extract_available_wilayas(data):
    available = {}
    if not data:
        return available

    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in ["data", "wilayas", "quotas", "results"]:
            if key in data:
                items = data[key]
                break
        if not items:
            items = [data]

    for item in items:
        if not isinstance(item, dict):
            continue

        wilaya_name = (
            item.get("wilaya_name") or
            item.get("wilaya") or
            item.get("name") or
            item.get("nom") or
            f"Wilaya {item.get('wilaya_id', item.get('id', '?'))}"
        )

        quota_available = (
            item.get("available_quota") or
            item.get("available") or
            item.get("remaining") or
            item.get("quota_restant") or
            item.get("quota_disponible") or
            0
        )

        quota_total = (
            item.get("total_quota") or
            item.get("total") or
            item.get("quota") or
            0
        )

        wilaya_id = item.get("wilaya_id") or item.get("id") or wilaya_name

        if quota_available and int(quota_available) > 0:
            available[str(wilaya_id)] = {
                "name": wilaya_name,
                "available": int(quota_available),
                "total": int(quota_total) if quota_total else 0
            }

    return available


async def send_notification(bot, message):
    # ① إرسال لك شخصياً
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        logger.info(f"Sent to personal chat {CHAT_ID}")
    except Exception as e:
        logger.error(f"Error sending to personal chat: {e}")

    # ② إرسال للقناة — مستقل عن الأول
    if CHANNEL_ID:
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            logger.info(f"Sent to channel {CHANNEL_ID}")
        except Exception as e:
            logger.error(f"Error sending to channel: {e}")


async def check_and_notify(bot, session):
    global previous_available

    logger.info("Checking wilaya quotas...")
    data = await fetch_quotas(session)

    if data is None:
        logger.warning("Could not fetch data from API")
        return

    current_available = extract_available_wilayas(data)

    newly_available = {
        wid: info for wid, info in current_available.items()
        if wid not in previous_available
    }

    increased = {
        wid: {**info, "prev": previous_available[wid]["available"]}
        for wid, info in current_available.items()
        if wid in previous_available and info["available"] > previous_available[wid]["available"]
    }

    now = datetime.now().strftime("%H:%M - %d/%m/%Y")

    if newly_available:
        msg = "🐑 <b>Moutons disponibles !</b>\n\n"
        for wid, info in newly_available.items():
            msg += f"📍 <b>{info['name']}</b>\n"
            msg += f"   Disponible : <b>{info['available']}"
            if info['total']:
                msg += f" / {info['total']}"
            msg += "</b>\n\n"
        msg += f"🔗 <a href='https://adhahi.dz'>Réserver maintenant</a>\n"
        msg += f"⏰ {now}"
        await send_notification(bot, msg)

    if increased:
        msg = "📈 <b>Plus de places disponibles !</b>\n\n"
        for wid, info in increased.items():
            msg += f"📍 <b>{info['name']}</b>\n"
            msg += f"   Avant : {info['prev']}  →  Maintenant : <b>{info['available']}</b>\n\n"
        msg += f"🔗 <a href='https://adhahi.dz'>Réserver maintenant</a>\n"
        msg += f"⏰ {now}"
        await send_notification(bot, msg)

    if current_available:
        logger.info(f"Available wilayas: {len(current_available)}")
    else:
        logger.info("No available wilayas at this time")

    previous_available = current_available


async def send_startup_message(bot):
    now = datetime.now().strftime("%H:%M - %d/%m/%Y")
    msg = "🤖 <b>Bot Adhahi démarré !</b>\n\n"
    msg += f"⏱ Vérification toutes les <b>{CHECK_INTERVAL}s</b>\n"
    msg += f"📢 Canal : {'✅ Activé' if CHANNEL_ID else '❌ Non configuré'}\n"
    msg += f"👤 Personnel : ✅ Activé\n"
    msg += f"⏰ {now}"
    await send_notification(bot, msg)


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required!")
    if not CHAT_ID:
        raise ValueError("CHAT_ID is required!")

    bot = Bot(token=BOT_TOKEN)
    logger.info("Starting Adhahi Bot...")
    await send_startup_message(bot)

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await check_and_notify(bot, session)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

            logger.info(f"Sleeping {CHECK_INTERVAL}s...")
            await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())