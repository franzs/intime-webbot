# intime-webbot

Webbot for entering timesheets from CSV to InTime using [Selenium](https://www.selenium.dev/) written in Python.

## Limitations

At the moment it is possible to enter a timesheet for the current month, only.

Only Firefox is supported.

## Prerequisites

### Webdriver for Selenium

Download [geckodriver](https://github.com/mozilla/geckodriver/releases) and install it for you operating system.

### Python packages

```bash
pip install -r requirements.txt
```

## Usage

Username and password have to be set via environment variables, e. g.

```bash
export INTIME_USERNAME="F.Lastname"
export INTIME_PASSWORD="2jWLJBv1vccU"
```

All other parameter can be set via environment variables or command line arguments:

| Environment variable       | Command line argument | Description                      | Default    |
| -------------------------- | --------------------- | -------------------------------- | ---------- |
| `INTIME_URL`               | `--url`               | Base URL of InTime               | &mdash;    |
| `INTIME_COLUMN_NAME_DATE`  | `--column-name-date`  | Name of date column in CSV file  | &mdash;    |
| `INTIME_COLUMN_NAME_TOTAL` | `--column-name-total` | Name of total column in CSV file | &mdash;    |
| `INTIME_CSV_FORMAT_DATE`   | `--csv-format-date`   | Name of pause column in CSV file | `%d.%m.%Y` |
| `INTIME_CSV_FORMAT_TIME`   | `--csv-format-time`   | Name of pause column in CSV file | `%H:%M`    |
| `INTIME_CSV_DELIMITER`     | `--csv-delimiter`     | Name of pause column in CSV file | `;`        |
| `INTIME_CSV_QUOTE_CHAR`    | `--csv-quote-char`    | Name of pause column in CSV file | `"`        |
| `INTIME_TIMESHEET_REF`     | `--timesheet-ref`     | UUID of timesheet for drafts     | &mdash;    |

For example:

```bash
export INTIME_URL="https://bureau6.es.rsmuk.com/"
```

Imagine you have a CSV file with the following content:

```
Datum;Tag;Ein;Aus;Pause;Total;Total (dezimal)
01.03.2021;Mo;08:00;17:00;01:00;08:00;08.00
```

Then you would set in addition:

```bash
export INTIME_COLUMN_NAME_DATE="Datum"
export INTIME_COLUMN_NAME_TOTAL="Total"
```

Finally you can execute the webbot:

```bash
./intime-webbot.py timesheet.csv
```
