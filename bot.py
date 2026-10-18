"""
Affiliate Alert Bot - v1 (Telegram, Rs 0 start)
- Admin posts deals with affiliate link -> bot formats + saves + posts to channel
- Users: /deals (latest deals), /track (price-drop track request), /coupon
- Har deal me "Affiliate Link" disclosure mandatory hai
- EarnKaro se Profit Link tumhe app me banana hai, bot us link ko hi share karega.
  Bot khud EarnKaro link nahi banata (EarnKaro ka public API nahi hai).
- Free hosting: Render free (15 min idle sleep) + SQLite. Data Render pe
  restart hone pe reset ho sakta hai, isliye v2 me Supabase use karenge.
"""
import os
import sqlite3
import logging
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")  # jaise @meradealchannel ya -100123...
DB_PATH = os.environ.get("DB_PATH", "deals.db")
MAX_DEALS_PER_DAY = 15  # spam se bachne ke liye, din me 15 se zyada deal mat post karo


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, new_price TEXT, old_price TEXT,
            link TEXT, category TEXT, created_at TEXT)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, link TEXT, target_price TEXT, created_at TEXT)"""
    )
    return conn


def is_admin(user_id: int) -> bool:
    return ADMIN_ID != 0 and user_id == ADMIN_ID


def format_deal(title, new_price, old_price, link, category):
    try:
        off = round((1 - float(new_price) / float(old_price)) * 100)
        off_txt = f" ({off}% OFF)"
    except Exception:
        off_txt = ""
    return (
        f"🔥 {title}\n\n"
        f"💰 Price: Rs {new_price} (MRP Rs {old_price}){off_txt}\n"
        f"📂 Category: {category}\n\n"
        f"👉 Buy here: {link}\n\n"
        f"⚠️ Affiliate Link - is link se kharidne pe hame thoda commission milta hai, "
        f"tumhe extra kuch nahi dena padta."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste! Main Deal Alert Bot hu. 🤖\n\n"
        "/deals - aaj ki latest deals dekho\n"
        "/track <product link> <target price> - price girne pe alert pao\n"
        "   Example: /track https://flipkart.com/... 499\n"
        "/coupon <category> - coupon dekho, jaise /coupon fashion\n"
        "/help - madad\n\n"
        "Deal channel ko join karo taaki koi loot miss na ho."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    rows = conn.execute(
        "SELECT title,new_price,old_price,link,category FROM deals ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("Abhi koi deal nahi hai. Thodi der baad /deals phir try karo.")
        return
    for title, new_price, old_price, link, category in rows:
        await update.message.reply_text(format_deal(title, new_price, old_price, link, category))


async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "Aise bhejo:\n/track <product link> <target price>\nExample:\n/track https://www.flipkart.com/... 499"
        )
        return
    link = context.args[0]
    target = context.args[1]
    conn = get_db()
    conn.execute(
        "INSERT INTO tracks (user_id, link, target_price, created_at) VALUES (?,?,?,?)",
        (update.effective_user.id, link, target, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    await update.message.reply_text(
        f"Done! ✅\nTumhara product track pe lag gaya hai.\nTarget price: Rs {target}\n"
        "Jab admin price update karega aur price target se neeche aayega, to tumhe batayenge.\n"
        "Note: v1 me price check admin karta hai, auto-scraping v2 me aayega."
    )


async def coupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = (context.args[0] if context.args else "all").lower()
    await update.message.reply_text(
        f"🎟️ Coupon - {cat}\n\n"
        "v1 me coupon list admin dalta hai. Abhi ke liye EarnKaro app me "
        "us category ke live coupon check karo aur yaha /deals me deal dekho.\n"
        "Admin: /postdeal se deal ke saath coupon code bhi title me likh sakta hai."
    )


async def postdeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin only. Format:
    /postdeal Title | new_price | old_price | affiliate_link | category
    Example: /postdeal Boat Earbuds | 499 | 999 | https://earnkaro.com/... | electronics
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Ye command sirf admin ke liye hai.")
        return
    text = update.message.text or ""
    try:
        payload = text.split(" ", 1)[1]
        title, new_price, old_price, link, category = [p.strip() for p in payload.split("|")]
    except Exception:
        await update.message.reply_text(
            "Format galat hai. Aise bhejo:\n"
            "/postdeal Title | new_price | old_price | affiliate_link | category\n\n"
            "Example:\n/postdeal Boat Earbuds | 499 | 999 | https://earnkaro.com/... | electronics"
        )
        return
    if "http" not in link:
        await update.message.reply_text("Link me http/https hona chahiye. EarnKaro se Profit Link bana ke paste karo.")
        return
    conn = get_db()
    today = datetime.now().date().isoformat()
    count = conn.execute(
        "SELECT COUNT(*) FROM deals WHERE substr(created_at,1,10)=?", (today,)
    ).fetchone()[0]
    if count >= MAX_DEALS_PER_DAY:
        conn.close()
        await update.message.reply_text(f"Aaj ke {MAX_DEALS_PER_DAY} deal ho gaye. Kal phir post karo, spam se bachna hai.")
        return
    conn.execute(
        "INSERT INTO deals (title,new_price,old_price,link,category,created_at) VALUES (?,?,?,?,?,?)",
        (title, new_price, old_price, link, category, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    msg = format_deal(title, new_price, old_price, link, category)
    # Channel pe bhejo agar set hai, nahi to admin ko hi bhejo
    if CHANNEL_ID:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
            await update.message.reply_text("Deal channel pe post ho gaya ✅")
        except Exception as e:
            logger.exception(e)
            await update.message.reply_text(f"Channel pe post fail hua: {e}\nDeal DB me save ho gaya, /deals me dikhega.")
    else:
        await update.message.reply_text("CHANNEL_ID set nahi hai, isliye deal sirf DB me save hua:\n\n" + msg)


def start_health_server():
    """Render free web service ka health check pass karne ke liye
    $PORT pe ek chhota HTTP server chalao. Polling bot khud koi port
    nahi kholta, isliye iske bina Render deploy ko 'In progress' me
    atka deta hai."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    port = int(os.environ.get("PORT", "10000"))
    try:
        server = HTTPServer(("0.0.0.0", port), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        logger.info("Health server on port %s", port)
    except Exception as e:
        logger.warning("Health server nahi chala: %s", e)


def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN env me set karo. .env.example dekho.")
    start_health_server()  # Render ka health check pass ho, isliye $PORT pe suno
    get_db().close()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("deals", deals))
    app.add_handler(CommandHandler("track", track))
    app.add_handler(CommandHandler("coupon", coupon))
    app.add_handler(CommandHandler("postdeal", postdeal))
    print("Affiliate Alert Bot running... /start se test karo")
    app.run_polling()


if __name__ == "__main__":
    main()
