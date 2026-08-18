import datetime
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

import requests
from bs4 import BeautifulSoup

CALENDAR_URL = "https://www.myfxbook.com/forex-economic-calendar"
RELEVANT_CURRENCIES = {"EUR", "GBP", "USD"}
REQUEST_TIMEOUT_SECONDS = 15


def fetch_events():
    """Retrieve and parse today's relevant economic-calendar events."""
    today_str = datetime.date.today().strftime("%b %d")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(
        CALENDAR_URL,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="economicCalendarTable")
    if table is None:
        raise RuntimeError(
            "Economic calendar table was not found; the source page structure may have changed."
        )

    events = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 6:
            continue

        event_time_full = cells[0].get_text(" ", strip=True)
        currency = cells[2].get_text(" ", strip=True)
        event_name = cells[3].get_text(" ", strip=True)
        forecast = cells[4].get_text(" ", strip=True)
        previous = cells[5].get_text(" ", strip=True)
        event_time = event_time_full.split("|")[0].strip()

        if today_str in event_time and currency in RELEVANT_CURRENCIES:
            events.append(
                {
                    "Time": event_time,
                    "Currency": currency,
                    "Impact": "N/A",
                    "Event": event_name,
                    "Forecast": forecast,
                    "Previous": previous,
                }
            )

    return events


def build_email_body(events):
    """Format parsed events as a plain-text email report."""
    if not events:
        return "No relevant EUR/GBP/USD economic-calendar events were found for today."

    lines = [
        "Today's Forex Events for EUR/GBP/USD",
        "Source: Myfxbook public economic calendar",
        "",
        "{:<20} {:<5} {:<8} {:<40} {:<12} {:<12}".format(
            "Time", "Curr", "Impact", "Event", "Forecast", "Previous"
        ),
    ]

    for event in events:
        lines.append(
            "{:<20} {:<5} {:<8} {:<40} {:<12} {:<12}".format(
                event["Time"][:20],
                event["Currency"][:5],
                event["Impact"][:8],
                event["Event"][:40],
                event["Forecast"][:12],
                event["Previous"][:12],
            )
        )

    return "\n".join(lines)


def get_email_config():
    """Load required SMTP configuration from environment variables."""
    config = {
        "from_email": os.getenv("FROM_EMAIL"),
        "to_email": os.getenv("TO_EMAIL"),
        "password": os.getenv("EMAIL_PASSWORD"),
    }

    missing = [name for name, value in config.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required email configuration: " + ", ".join(missing)
        )

    return config


def send_email(body, config):
    """Send the formatted report using Gmail SMTP over TLS."""
    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = (
        f"Daily Forex Events - {datetime.date.today().strftime('%Y-%m-%d')}"
    )
    message["From"] = config["from_email"]
    message["To"] = config["to_email"]

    tls_context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.ehlo()
        server.starttls(context=tls_context)
        server.ehlo()
        server.login(config["from_email"], config["password"])
        server.send_message(message)


def main():
    try:
        events = fetch_events()
        email_body = build_email_body(events)
        email_config = get_email_config()
        send_email(email_body, email_config)
        print(f"Email sent successfully with {len(events)} matching event(s).")
        return 0
    except requests.RequestException as error:
        print(f"Calendar retrieval failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"ForexSentinel failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
