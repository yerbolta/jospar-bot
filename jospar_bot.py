"""
JOSPAR — Telegram Bot
/ok <nomer> — ssylka na skachivanie
/leads     — poslednie zayavki
"""

import requests
import os
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8935289424:AAFgsfrBMWZx_7zvVvnWlh_qU2kprueYj1c")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID", "217420681")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://vperfytwmwrffkgkiwqz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwZXJmeXR3bXdyZmZrZ2tpd3F6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2NTk3OTcsImV4cCI6MjA5NzIzNTc5N30.xx8OBH_BLeTyRs75FfpxyUbHze3qcq3gpIutLjMDb7E")

BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
SESSION = requests.Session()


def send(chat_id, text):
    try:
        SESSION.post(f"{BASE}/sendMessage", json={
            "chat_id": chat_id, "text": text, "parse_mode": "HTML"
        }, timeout=10)
    except Exception as e:
        print(f"send error: {e}")


def get_project(num):
    try:
        r = SESSION.get(
            f"{SUPABASE_URL}/rest/v1/projects",
            params={"id": f"like.{num}%", "select": "id,name,area,price"},
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=10
        )
        rows = r.json()
        return rows[0] if rows else None
    except Exception as e:
        print(f"supabase error: {e}")
        return None


def get_signed_url(folder, filename, expires=172800):
    try:
        r = SESSION.post(
            f"{SUPABASE_URL}/storage/v1/object/sign/plans/{folder}/{filename}",
            json={"expiresIn": expires},
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=10
        )
        data = r.json()
        signed = data.get("signedURL") or data.get("signedUrl") or data.get("signed_url")
        if signed:
            return f"{SUPABASE_URL}/storage/v1{signed}" if not signed.startswith("http") else signed
        return None
    except Exception as e:
        print(f"signed url error: {e}")
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

    pdf_url = get_signed_url(folder, "full.pdf")
    dwg_url = get_signed_url(folder, "full.dwg")

    if not pdf_url:
        send(OWNER_CHAT_ID, f"Oshibka: fayly dlya №{num} ne naydeny v Supabase")
        return

    text = f"Oplata podtverzhdena - №{num}\n{caption}\nSsylki dlya klienta (48 chasov):\n\nPDF: {pdf_url}\n\nDWG: {dwg_url or '—'}\n\nSkopiruy i otprav klientu v WhatsApp"
    send(OWNER_CHAT_ID, text)


def poll():
    offset = 0
    print("JOSPAR bot started.")
    send(OWNER_CHAT_ID, "JOSPAR bot zapushchen.\n/ok 1 - ssylka na plan №001\n/leads - poslednie zayavki")

    while True:
        try:
            r = SESSION.get(
                f"{BASE}/getUpdates",
                params={"offset": offset, "timeout": 20, "allowed_updates": ["message"]},
                timeout=25
            )
            updates = r.json().get("result", [])

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
                        send(OWNER_CHAT_ID, "Ukazi nomer: /ok 1")
                    else:
                        handle_ok(parts[1])

                elif text == "/leads":
                    send(OWNER_CHAT_ID, "Zayavki: smotri leads.json")

        except KeyboardInterrupt:
            print("Bot stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    poll()
# redeploy
