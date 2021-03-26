#!/usr/bin/env python

import argparse
import csv
import datetime
import os
import re
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


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
    return str(int((float(total) + 7 / 60) / 0.25) * 0.25)


def enter_day(date, total):
    xpath = f"(//td[span[contains(text(), '{date}')]]/following-sibling::td)[1]/select"
    elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    select = Select(elem)
    select.select_by_visible_text('Stunde(n) Remote')

    xpath = f"(//td[span[contains(text(), '{date}')]]/following-sibling::td)[6]/input"
    elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    elem.clear()
    elem.send_keys(total)

    steal_focus()


def steal_focus():
    driver.find_element_by_xpath("//body").click()


parser = argparse.ArgumentParser(description='Import timesheet to InTime')
parser.add_argument('filename', help='Filename of timesheet')
parser.add_argument('--url',               default=os.environ.get('INTIME_URL'))
parser.add_argument('--column-name-date',  default=os.environ.get('INTIME_COLUMN_NAME_DATE'))
parser.add_argument('--column-name-total', default=os.environ.get('INTIME_COLUMN_NAME_TOTAL'))
parser.add_argument('--csv-delimiter',     default=os.environ.get('INTIME_CSV_DELIMITER', ';'))
parser.add_argument('--csv-quote-char',    default=os.environ.get('INTIME_CSV_QUOTE_CHAR', '"'))

args = parser.parse_args()
if not args.url or not args.column_name_date or not args.column_name_total:
    exit(parser.print_usage())

if not os.environ.get('INTIME_USERNAME') or not os.environ.get('INTIME_PASSWORD'):
    exit("Set environment variables INTIME_USERNAME and INTIME_PASSWORD.")

now = datetime.datetime.now()

profile = webdriver.FirefoxProfile()

driver = webdriver.Firefox(profile)
wait = WebDriverWait(driver, 10)
driver.get(args.url + 'timesheetEntry/webEntry')

wait.until(EC.title_is('Intime'))

login(os.environ['INTIME_USERNAME'], os.environ['INTIME_PASSWORD'])

try:
    wait.until(EC.title_is('Timesheet'))
except TimeoutException:
    driver.close()
    exit("Login failed.")

select = Select(driver.find_element_by_name('selectedPlacement'))
select.select_by_index(1)

elem = wait.until(EC.presence_of_element_located((By.ID, 'timesheetDate')))
elem.click()
elem.clear()
elem.send_keys(now.strftime('%d/%m/%Y'))

steal_focus()

with open(args.filename, newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=args.csv_delimiter, quotechar=args.csv_quote_char)

    for row in csvreader:
        if not re.search(r'^\d+', row[args.column_name_date]):
            break

        date = datetime.datetime.strptime(row[args.column_name_date], '%d.%m.%Y')

        if date.month != now.month or date.year != now.year:
            print(f"row {row} is not in current month. Ignoring.", file=sys.stderr)
            continue

        enter_day(date.strftime('%d/%m/%Y'), procon_round(row[args.column_name_total]))

driver.close()
