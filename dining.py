import sys
import time
import requests
from datetime import datetime, timedelta

NTFY_TOPIC = "jarvis-patrick"

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
    "Acorn Coffee Shop": [("09:00", "14:00", "Open")],
    "Fountain Market": [("13:00", "17:00", "Open")],
    "Qdoba Mexican Grill": [("12:00", "25:00", "Open")],
    "Einstein Bros. Bagels": [("09:00", "14:00", "Open")],
    "Biscuitville": [("08:00", "25:00", "Open")],
    "Flat Out": [("11:00", "25:00", "Open")],
    "Freshii": [("11:00", "20:00", "Open")],
}

MAIN_HALLS = ["McEwen Food Hall", "Lakeside Dining Hall"]


def get_eastern_time():
    utc_now = datetime.utcnow()
    offset = 4 if 3 <= utc_now.month <= 11 else 5
    return utc_now - timedelta(hours=offset)


def parse_time(t_str, now):
    h, m = map(int, t_str.split(":"))
    if h >= 24:
        h -= 24
        return datetime(now.year, now.month, now.day, h, m) + timedelta(days=1)
    return datetime(now.year, now.month, now.day, h, m)


def send_notification(title, message, priority="default"):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message,
            headers={
                "Title": title,
                "Priority": priority,
                "Tags": "fork_and_knife"
            }
        )
        print(f"[Jarvis] Sent: {title}")
    except Exception as e:
        print(f"[Jarvis] Error: {e}")


def send_morning_summary():
    now = get_eastern_time()
    msg = (
        f"Good morning! Today's hours:\n"
        f"McEwen: Brunch 9am-2pm, Dinner 4:30-8pm\n"
        f"Lakeside: Brunch 10am-2pm, Dinner 5-9pm, Late Night 10pm-1am\n"
        f"Qdoba: 12pm-1am | Biscuitville: 8am-1am\n"
        f"Einstein: 9am-2pm | Freshii: 11am-8pm"
    )
    send_notification("Jarvis: Dining Hours", msg)


def show_hours():
    now = get_eastern_time()
    print("\n" + "="*52)
    print("  JARVIS - ELON DINING HOURS")
    print(f"  {now.strftime('%A, %B %d at %I:%M %p')}")
    print("="*52)
    for name, sessions in LOCATIONS.items():
        is_main = name in MAIN_HALLS
        prefix = "★ " if is_main else "  "
        print(f"\n{prefix}{name}")
        for open_t, close_t, label in sessions:
            open_dt = parse_time(open_t, now)
            close_dt = parse_time(close_t, now)
            if open_dt <= now <= close_dt:
                mins_left = int((close_dt - now).total_seconds() / 60)
                status = f"OPEN NOW - closes in {mins_left} min"
            elif now < open_dt:
                mins_until = int((open_dt - now).total_seconds() / 60)
                status = f"Opens in {mins_until} min" if mins_until < 60 else f"Opens at {open_dt.strftime('%I:%M %p')}"
            else:
                status = f"Closed ({label})"
            print(f"     {label}: {open_dt.strftime('%I:%M %p')} - {close_dt.strftime('%I:%M %p')}  [{status}]")
    print("\n" + "="*52 + "\n")


def watch():
    print("[Jarvis] Dining watcher running. Notifications at 15 and 5 min before open/close.")
    print("[Jarvis] Press Ctrl+C to stop.\n")
    notified = set()
    while True:
        now = get_eastern_time()
        for name, sessions in LOCATIONS.items():
            for open_t, close_t, label in sessions:
                open_dt = parse_time(open_t, now)
                close_dt = parse_time(close_t, now)
                diff_open = (open_dt - now).total_seconds() / 60
                diff_close = (close_dt - now).total_seconds() / 60

                open_key_15 = f"{name}_{label}_open15_{now.date()}"
                if 14 <= diff_open <= 15 and open_key_15 not in notified:
                    send_notification(f"{name} opens soon", f"{label} opens in 15 min at {open_dt.strftime('%I:%M %p')}", "high")
                    notified.add(open_key_15)

                open_key_5 = f"{name}_{label}_open5_{now.date()}"
                if 4 <= diff_open <= 5 and open_key_5 not in notified:
                    send_notification(f"{name} opens NOW", f"{label} opens in 5 min at {open_dt.strftime('%I:%M %p')}", "urgent")
                    notified.add(open_key_5)

                close_key_15 = f"{name}_{label}_close15_{now.date()}"
                if 14 <= diff_close <= 15 and close_key_15 not in notified:
                    send_notification(f"{name} closes soon", f"{label} closes in 15 min at {close_dt.strftime('%I:%M %p')}", "high")
                    notified.add(close_key_15)

                close_key_5 = f"{name}_{label}_close5_{now.date()}"
                if 4 <= diff_close <= 5 and close_key_5 not in notified:
                    send_notification(f"{name} closing NOW", f"{label} closes in 5 min at {close_dt.strftime('%I:%M %p')}", "urgent")
                    notified.add(close_key_5)

        time.sleep(60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        send_morning_summary()
        show_hours()
        watch()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        send_notification("Jarvis Test", "Notifications are working!")
    else:
        show_hours()
