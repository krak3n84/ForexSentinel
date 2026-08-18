# ForexSentinel

A lightweight Python automation project that retrieves public economic-calendar data, filters events relevant to selected currencies, and emails a daily summary.

The project is primarily an example of **scheduled data retrieval, HTML parsing, environment-based configuration, and SMTP delivery**. It does not predict market direction or provide trading guarantees.

![Successful Email Send Output](./email_sent_screenshot.jpg)

## Features

- Retrieves the public Myfxbook economic calendar with `requests`
- Parses calendar rows with Beautiful Soup
- Filters events for configured currencies (`EUR`, `GBP`, and `USD` by default)
- Formats matching events into a readable text summary
- Sends the report through Gmail SMTP using TLS
- Reads email credentials from environment variables rather than hard-coding them in the script
- Works well with Windows Task Scheduler or another external scheduler

## Requirements

- Python 3.10+
- `requests`
- `beautifulsoup4`

Install dependencies:

```bash
python -m pip install requests beautifulsoup4
```

## Setup

Clone the repository:

```bash
git clone https://github.com/krak3n84/ForexSentinel.git
cd ForexSentinel
```

Set the following environment variables before running the script:

- `FROM_EMAIL` — Gmail address used to send the summary
- `TO_EMAIL` — destination email address
- `EMAIL_PASSWORD` — Gmail app password or other supported SMTP credential

Do not commit credentials, app passwords, or `.env` files containing secrets.

## Usage

```bash
python daily_forex_events.py
```

The script attempts to retrieve the day's public calendar entries, filters for the configured currencies, and sends either a formatted event summary or a no-events message.

## Automation

The script itself runs once and exits. For recurring execution, use an external scheduler such as:

- Windows Task Scheduler
- cron
- a CI/CD scheduler
- another approved automation platform

This separation keeps scheduling logic outside the data-processing script.

## Security Notes

- Credentials are loaded from environment variables.
- SMTP transport uses TLS.
- Gmail app passwords are preferable to storing a primary account password.
- Public web-page structure can change; parsing failures should be treated as data-source failures rather than valid empty results.
- Review the source site's terms and access policies before increasing request frequency.

## Limitations

- The parser depends on the current HTML structure of the source page.
- The script currently treats event impact as `N/A` because the parsed table structure does not expose a reliable impact field in the implemented path.
- This project summarizes public calendar information only; it does not perform forecasting, trade execution, or investment advice.

## License

MIT License. See [LICENSE](LICENSE).

## Purpose

I built this as a practical automation exercise: retrieve external data, filter it into an operator-relevant subset, handle credentials more safely, and deliver the result on a repeatable schedule.
