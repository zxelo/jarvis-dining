import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

GMAIL_USER = "graphyyt@gmail.com"
GMAIL_APP_PASSWORD = "lmzbmpmknzrtazbi"
SMS_ADDRESS = "2039040516@vtext.com"

LOCATIONS = {
    "McEwen Food Hall": [
        ("09:00", "14:00", "Brunch"),
        ("16:30", "20:00", "Dinner"),
    ],
    "Lakeside Dining Hall": [
        ("10:00", "14:00", "Brunch"),
        ("17:00", "21:00", "Dinner"),
        ("22:00", "25:00", "Late Night"),
    ],
    "Acorn Coffee Shop": [
        ("09:00", "14:00", "Open"),
    ],
    "Fountain Market": [
        ("13:00", "17:00", "Open"),
    ],
    "Qdoba Mexican Grill": [
        ("12:00", "25:00", "Open"),
    ],
    "Einstein Bros. Bagels": [
        ("09:00", "14:00", "Open"),
    ],
    "Biscuitville": [
        ("08:00", "25:00", "Open"),
    ],
    "Flat Out": [
        ("11:00", "25:00", "Open"),
    ],
    "Freshii": [
        ("11:00", "20:00", "Open"),
    ],
}


def get_eastern_time():
    return datetime.utcnow() - timedelta(hours=4)


def parse_time(t_str, now):
    h, m = map(int, t_str.split(":"))
    if h >= 24:
        h -= 24
        return datetime(now.year, now.month, now.day, h, m) + timedelta(days=1)
    return datetime(now.year, now.month, now.day, h, m)


def send_sms(title, message):
    try:
        msg = MIMEText(f"{title}\n{message}")
        msg["From"] = GMAIL_USER
        msg["To"] = SMS_ADDRESS
        msg["Subject"] = title
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, SMS_ADDRESS, msg.as_string())
        print(f"[Jarvis] Text sent: {title}")
    except Exception as e:
        print(f"[Jarvis] SMS error: {e}")


def run():
    now = get_eastern_time()
    print(f"[Jarvis] Checking at {now.strftime('%I:%M %p')} Eastern")

    for name, sessions in LOCATIONS.items():
        for open_t, close_t, label in sessions:
            open_dt = parse_time(open_t, now)
            close_dt = parse_time(close_t, now)
            diff_open = (open_dt - now).total_seconds() / 60
            diff_close = (close_dt - now).total_seconds() / 60

            if 14 <= diff_open <= 15:
                send_sms(f"Jarvis: {name} opens soon", f"{label} opens in 15 min at {open_dt.strftime('%I:%M %p')}")

            if 4 <= diff_open <= 5:
                send_sms(f"Jarvis: {name} opens NOW", f"{label} opens in 5 min at {open_dt.strftime('%I:%M %p')}")

            if 14 <= diff_close <= 15:
                send_sms(f"Jarvis: {name} closes soon", f"{label} closes in 15 min at {close_dt.strftime('%I:%M %p')}")

            if 4 <= diff_close <= 5:
                send_sms(f"Jarvis: {name} closing NOW", f"{label} closes in 5 min at {close_dt.strftime('%I:%M %p')}")


if __name__ == "__main__":
    send_sms("Jarvis Test", "GitHub Actions is working!")
    run()
