#!/usr/bin/env python

import argparse
import csv
import os
import re
import sys

from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

DEFAULT_CSV_FORMAT_DATE = '%d.%m.%Y'
DEFAULT_CSV_FORMAT_TIME = '%H:%M'
DEFAULT_CSV_DELIMITER = ';'
DEFAULT_CSV_QUOTE_CHAR = '"'

INTIME_DATE_FORMAT = '%d/%m/%Y'


def login(username, password):
    elem = wait.until(EC.presence_of_element_located((By.ID, 'j_username')))
    elem.clear()
    elem.send_keys(username)

    elem = wait.until(EC.presence_of_element_located((By.ID, 'j_password')))
    elem.clear()
    elem.send_keys(password)

    elem = wait.until(EC.presence_of_element_located((By.ID, 'login-submit')))
    elem.click()


def procon_round(total):
    total_minutes = total.hour * 60 + total.minute
    rounded_minutes = int((total_minutes + 7) / 15) * 15
    rounded_hours = rounded_minutes / 60

    return str(rounded_hours)


def enter_day(date, total):
    date_str = date.strftime(INTIME_DATE_FORMAT)

    xpath = f"(//td[span[contains(text(), '{date_str}')]]/following-sibling::td)[1]/select"
    elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    select = Select(elem)
    select.select_by_visible_text('Stunde(n) Remote')

    xpath = f"(//td[span[contains(text(), '{date_str}')]]/following-sibling::td)[6]/input"
    elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    elem.clear()
    elem.send_keys(total)

    steal_focus()


def steal_focus():
    driver.find_element_by_xpath("//body").click()


def argument_options(key, default=None):
    default_value = os.environ.get(key, default)

    map = {'default': default_value} if default_value else {'required': True}

    return map


parser = argparse.ArgumentParser(description='Import timesheet to InTime')
parser.add_argument('filename', help='Filename of timesheet')
parser.add_argument('--url',               **argument_options('INTIME_URL'))
parser.add_argument('--timesheet-ref',     default=os.environ.get('INTIME_TIMESHEET_REF'))
parser.add_argument('--column-name-date',  **argument_options('INTIME_COLUMN_NAME_DATE'))
parser.add_argument('--column-name-total', **argument_options('INTIME_COLUMN_NAME_TOTAL'))
parser.add_argument('--csv-format-date',   **argument_options('INTIME_CSV_FORMAT_DATE', DEFAULT_CSV_FORMAT_DATE))
parser.add_argument('--csv-format-time',   **argument_options('INTIME_CSV_FORMAT_TIME', DEFAULT_CSV_FORMAT_TIME))
parser.add_argument('--csv-delimiter',     **argument_options('INTIME_CSV_DELIMITER', DEFAULT_CSV_DELIMITER))
parser.add_argument('--csv-quote-char',    **argument_options('INTIME_CSV_QUOTE_CHAR', DEFAULT_CSV_QUOTE_CHAR))

args = parser.parse_args()
if not args.url or not args.column_name_date or not args.column_name_total:
    exit(parser.print_usage())

if not os.environ.get('INTIME_USERNAME') or not os.environ.get('INTIME_PASSWORD'):
    exit("Set environment variables INTIME_USERNAME and INTIME_PASSWORD.")

now = datetime.now()

profile = webdriver.FirefoxProfile()

driver = webdriver.Firefox(profile)
wait = WebDriverWait(driver, 10)

if not args.url.endswith('/'):
    args.url += '/'

if args.timesheet_ref:
    driver.get(args.url + f'timesheetEntry/webEntry?timesheetRef={args.timesheet_ref}')
else:
    driver.get(args.url + 'timesheetEntry/webEntry')

wait.until(EC.title_is('Intime'))

login(os.environ['INTIME_USERNAME'], os.environ['INTIME_PASSWORD'])

try:
    wait.until(EC.title_is('Timesheet'))
except TimeoutException:
    driver.close()
    exit("Login failed.")

if not args.timesheet_ref:
    select = Select(driver.find_element_by_name('selectedPlacement'))
    select.select_by_index(1)

    elem = wait.until(EC.presence_of_element_located((By.ID, 'timesheetDate')))
    elem.click()
    elem.clear()
    elem.send_keys(now.strftime(INTIME_DATE_FORMAT))

    steal_focus()

with open(args.filename, newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=args.csv_delimiter, quotechar=args.csv_quote_char)

    for row in csvreader:
        if not re.search(r'^\d+', row[args.column_name_date]):
            break

        date = datetime.strptime(row[args.column_name_date], args.csv_format_date)

        if date.month != now.month or date.year != now.year:
            print(f"row {row} is not in current month. Ignoring.", file=sys.stderr)
            continue

        total = datetime.strptime(row[args.column_name_total], args.csv_format_time)
        total_rounded = procon_round(total)

        enter_day(date, total_rounded)

xpath = f"//input[@value='Save As Draft']"
elem = driver.find_element_by_xpath(xpath)
elem.click()

driver.close()
