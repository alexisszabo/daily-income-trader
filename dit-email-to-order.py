import os
import re
import datetime as dt
import time
from db.models import Order
from mail import (
  get_mailbox,
  get_mail_client,
  get_emails_after
)
from jmapc import Email

date_last_order_placed = None

def main():
  print("Waiting for Email...")
  while True:
    today = dt.datetime.today().date()
    if date_last_order_placed != today:
      now = dt.datetime.now().time()
      time_window_start = dt.time(6, 0, 0)
      time_window_end = dt.time(7, 0, 0)
      if time_window_start < now < time_window_end:
        check_for_new_emails()
    time.sleep(60)

def check_for_new_emails():
  client = get_mail_client(os.environ["JMAP_HOST"], os.environ["JMAP_API_TOKEN_DIT"])
  mailbox = get_mailbox(client, os.environ["JMAP_FOLDER_NAME_DIT"])
  emails = get_emails_after(client, mailbox, dt.datetime.today())
  #emails = get_emails_after(client, mailbox, dt.datetime(2023, 12, 12))

  for email in emails:
    match = re.search(r"Tim Bohen's Daily Market Profits Alert - ([0-9]+/[0-9]+/[0-9]+)", email.subject)
    if not match:
      print(f"email.subject '{email.subject}' did not match")
      continue 
    date = dt.datetime.strptime(match.group(1), "%m/%d/%y") 
    if dt.datetime.today().date() != date.date():
      print("Date did not match ()")
      continue
    process_email(email)

def process_email(email: Email):
  text_body = email.body_values['1'].value

  ticker = ''
  signal_price = 0.0 
  target_price = 0.0
  stop_loss_price = 0.0 

  for line in text_body.splitlines():
    match = re.search(r"Today’s Daily Market Profit Alerts is \$([A-z]+)", line)
    if match:
      ticker = match.group(1)

    match = re.search(r"^Signal Price:.*\$(([0-9]+)(\.[0-9]+)?).*$", line)
    if match:
      signal_price = float(match.group(1))

    match = re.search(r"^Target Price:.*\$(([0-9]+)(\.[0-9]+)?).*$", line)
    if match:
      target_price = float(match.group(1))
      if (target_price % 1 == 0 and re.search("high", line, re.IGNORECASE)):
        target_price += 0.80

    match = re.search(r"^Stop Loss Price:.*\$(([0-9]+)(\.[0-9]+)?).*$", line)
    if match:
      stop_loss_price = float(match.group(1))

  parsed_values_seem_reasonable = (
    ticker != '' and
    signal_price > 0 and
    target_price > 0 and
    stop_loss_price > 0 and
    stop_loss_price < signal_price < target_price
  )

  print("-------------------")
  print("Parsed Today's Daily Profits Alert Email")
  print(f"Ticker: ${ticker}")
  print(f"Signal Price: ${signal_price}")
  print(f"Target Price: ${target_price}")
  print(f"Stop Loss Price: ${stop_loss_price}")

  if not parsed_values_seem_reasonable:
    return

  # Do some sanity checking to make sure the numbers are reasonable.
  profit_difference = target_price - signal_price
  stop_loss_difference = signal_price - stop_loss_price

  MINIMUM_RISK_TO_REWARD_RATIO = 2
  risk_to_reward_ratio = profit_difference / stop_loss_difference
  exceeds_target_risk_to_reward_ratio = risk_to_reward_ratio >= MINIMUM_RISK_TO_REWARD_RATIO

  # TO DO: Add other criteria here:
  values_seem_reasonable = (
    exceeds_target_risk_to_reward_ratio
  )

  if not values_seem_reasonable:
    return

  today = dt.datetime.today()

  matching_orders = Order.objects.filter(ticker=ticker, date=today)

  if matching_orders.count() > 0:
    return

  print('creating order')
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
