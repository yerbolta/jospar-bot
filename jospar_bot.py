"""
JOSPAR — Telegram Bot
/ok <nomer> — ssylka na skachivanie
/leads     — poslednie zayavki
"""

import urllib.request
import urllib.parse
import json
import os
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8770606231:AAHbggvbON7G6HUHMV80KhI7Q6lBQ0jO8BI")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID", "217420681")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://vperfytwmwrffkgkiwqz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwZXJmeXR3bXdyZmZrZ2tpd3F6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2NTk3OTcsImV4cCI6MjA5NzIzNTc5N30.xx8OBH_BLeTyRs75FfpxyUbHze3qcq3gpIutLjMDb7E")


def api(method, data=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"API error {method}: {e}")
        return {}


def send(chat_id, text):
    api("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def get_project(num):
    url = f"{SUPABASE_URL}/rest/v1/projects?id=like.{num}%25&select=id,name,area,price"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            rows = json.loads(r.read())
            return rows[0] if rows else None
    except Exception as e:
        print(f"Supabase error: {e}")
        return None


def handle_ok(project_num):
    num = project_num.zfill(3)
    project = get_project(num)

    if project:
        name = project.get("name", "")
        area = project.get("area", "")
        price = project.get("price", 0)
        folder = project["id"]
        caption = f"{name}, {area} m2 | {price:,} T\n"
    else:
        folder = num
        caption = ""

    download_page = f"https://jospar.vercel.app/download/{folder}"

    text = f"Oplata podtverzhdena - №{num}\n{caption}\nSsylka dlya klienta:\n{download_page}\n\nSkopiruy i otprav klientu v WhatsApp"
    send(OWNER_CHAT_ID, text)


def poll():
    offset = 0
    print("JOSPAR bot started.")
    send(OWNER_CHAT_ID, "JOSPAR bot zapushchen.\n/ok <nomer> - ssylka na skachivanie\n/leads - zayavki")

    while True:
        try:
            result = api("getUpdates", {"offset": offset, "timeout": 30, "allowed_updates": ["message"]})
            updates = result.get("result", [])

            for upd in updates:
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "").strip()

                if chat_id != OWNER_CHAT_ID:
                    continue

                if text.startswith("/ok"):
                    parts = text.split()
                    if len(parts) < 2:
                        send(OWNER_CHAT_ID, "Ukazi nomer proekta: /ok 15")
                    else:
                        handle_ok(parts[1])

                elif text == "/leads":
                    send(OWNER_CHAT_ID, "Zayavki: smotri leads.json na servere")

        except KeyboardInterrupt:
            print("Bot stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    poll()
