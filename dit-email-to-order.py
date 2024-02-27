import os
import re
import datetime as dt
import math
import time
from db.models import Order
from mail import (
  get_mailbox,
  get_mail_client,
  get_emails_after
)
from jmapc import Email

date_last_order_placed = None
MINIMUM_RISK_TO_REWARD_RATIO = 2

def main():
  print("Waiting for Email...")
  while True:
    today = dt.datetime.today().date()
    if date_last_order_placed != today:
      now = dt.datetime.now().time()
      time_window_start = dt.time(6, 0, 0)
      time_window_end = dt.time(8, 0, 0)
      if time_window_start < now < time_window_end:
        check_for_new_emails()
    time.sleep(60)

def check_for_new_emails():
  client = get_mail_client(os.environ["JMAP_HOST"], os.environ["JMAP_API_TOKEN_DIT"])
  mailbox = get_mailbox(client, os.environ["JMAP_FOLDER_NAME_DIT"])
  emails = get_emails_after(client, mailbox, dt.datetime.today())
  #emails = get_emails_after(client, mailbox, dt.datetime(2023, 12, 12))

  for email in emails:
    # Auto email from Tim Bohen
    match = re.search(r"Tim Bohen's Daily Market Profits Alert - ([0-9]+/[0-9]+/[0-9]+)", email.subject)

    # Manually sent emil from myself
    match_manual = re.search(r"Daily Income Trader Manual Entry", email.subject)

    if not match and not match_manual:
      print(f"email.subject '{email.subject}' did not match")
      continue 

    today = dt.datetime.today().date()

    if match:
      date = dt.datetime.strptime(match.group(1), "%m/%d/%y") 
      if today != date.date():
        print("Date did not match ()")
        continue

    if match_manual:
      if email.date.date() != today:
        print("Date did not match")
        continue

    process_email(email)

def process_email(email: Email):
  text_body = email.body_values['1'].value

  ticker = ''
  signal_price = 0.0 
  target_price = 0.0
  stop_loss_price = 0.0 
  target_has_the_word_high = False

  for line in text_body.splitlines():
    match = re.search(r"Today’s Daily Market Profit Alerts is \$([A-z]+)", line)
    if match:
      ticker = match.group(1)

    match = re.search(r"Signal Price:.*\$\s*(([0-9]+)(\.[0-9]+)?).*$", line)
    if match:
      signal_price = float(match.group(1))

    match = re.search(r"Target Price:[^$]*\$\s*(([0-9]+)(\.[0-9]+)?).*$", line)
    if match:
      target_price = float(match.group(1))
      if (target_price % 1 == 0 and re.search(r"high \$\s*" + match.group(1), line, re.IGNORECASE)):
        target_has_the_word_high = True

    match = re.search(r"Stop Loss Price:.*\$\s*(([0-9]+)(\.[0-9]+)?).*$", line)
    if match:
      stop_loss_price = float(match.group(1))

  parsed_values_seem_reasonable = (
    ticker != '' and
    signal_price > 0 and
    target_price > 0 and
    stop_loss_price > 0
  )

  # Calculate target price based on risk/reward ratio, and use that if it is in the $ range of the target
  # ie. if the price could be in the "high $1", accept a target price anywhere between $1.00 and $1.99
  if parsed_values_seem_reasonable and target_has_the_word_high:
    risk = signal_price - stop_loss_price
    reward = risk * MINIMUM_RISK_TO_REWARD_RATIO
    potential_target = signal_price + reward
    if (potential_target >= signal_price) and potential_target < (math.floor(signal_price) + 1):
      print(f"Calculated target prices based on {MINIMUM_RISK_TO_REWARD_RATIO}:1 risk/reward ratio")
      target_price = potential_target

  print("-------------------")
  print("Parsed Today's Daily Profits Alert Email")
  print(f"Ticker: ${ticker}")
  print(f"Signal Price: ${signal_price}")
  print(f"Target Price: ${target_price}")
  print(f"Stop Loss Price: ${stop_loss_price}")

  # More sanity checking
  parsed_values_seem_reasonable = parsed_values_seem_reasonable and (stop_loss_price < signal_price < target_price)

  if not parsed_values_seem_reasonable:
    print("*** Skipping. Parsed numbers do not seem reasonable")
    return

  # Do some sanity checking to make sure the numbers are reasonable.
  profit_difference = target_price - signal_price
  stop_loss_difference = signal_price - stop_loss_price

  risk_to_reward_ratio = profit_difference / stop_loss_difference
  exceeds_target_risk_to_reward_ratio = risk_to_reward_ratio >= MINIMUM_RISK_TO_REWARD_RATIO

  if not exceeds_target_risk_to_reward_ratio:
    print(f"*** Skipping. Does not exceed target risk to reward ratio of {MINIMUM_RISK_TO_REWARD_RATIO}")
    return

  today = dt.datetime.today()

  matching_orders = Order.objects.filter(ticker=ticker, date=today)

  if matching_orders.count() > 0:
    print("Order already created")
    return

  print('*** Creating Order!')
  order = Order(
    date=today,
    ticker=ticker,
    signal_price=signal_price,
    target_price=target_price,
    stop_loss_price=stop_loss_price
  ) 
  order.save()
  global date_last_order_placed
  date_last_order_placed = dt.datetime.today().date()

if __name__ == "__main__":
  main()
