import os
import re
import datetime as dt
from db.models import Order
from mail import (
  get_mailbox,
  get_mail_client,
  get_emails_after
)

client = get_mail_client(os.environ["JMAP_HOST"], os.environ["JMAP_API_TOKEN_DIT"])
mailbox = get_mailbox(client, os.environ["JMAP_FOLDER_NAME_DIT"])
emails = get_emails_after(client, mailbox, dt.datetime.today())
#emails = get_emails_after(client, mailbox, dt.datetime(2023, 12, 12))

n_emails = len(emails.data)

if (n_emails == 1):
  email = emails.data[0]
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

    match = re.search(r"^Stop Loss Price:.*\$(([0-9]+)(\.[0-9]+)?).*$", line)
    if match:
      stop_loss_price = float(match.group(1))

  if (
       ticker != '' and
       signal_price > 0 and
       target_price > 0 and
       stop_loss_price > 0 and
       stop_loss_price < signal_price < target_price
     ):
    print("Parsed Today's Daily Profits Alert Email")
    print(f"Ticker: ${ticker}")
    print(f"Signal Price: ${signal_price}")
    print(f"Target Price: ${target_price}")
    print(f"Stop Loss Price: ${stop_loss_price}")

    # Do some sanity checking to make sure the numbers are reasonable.
    profit_difference = target_price - signal_price
    stop_loss_difference = signal_price - stop_loss_price

    MINIMUM_RISK_TO_REWARD_RATIO = 2
    risk_to_reward_ratio = profit_difference / stop_loss_difference
    exceeds_target_risk_to_reward_ratio = risk_to_reward_ratio >= MINIMUM_RISK_TO_REWARD_RATIO

    # TO DO: Add other criteria here:
    okay_to_write_to_database = exceeds_target_risk_to_reward_ratio

    if okay_to_write_to_database:
      print('okay to write to database')
      today = dt.datetime.today()

      matching_orders = Order.objects.filter(ticker=ticker, date=today)

      if matching_orders.count() == 0:
        print('creating order')
        order = Order(
          date=today,
          ticker=ticker,
          signal_price=signal_price,
          target_price=target_price,
          stop_loss_price=stop_loss_price
        ) 
        order.save()

elif (n_emails > 0):
  print('Found more emails than expected')
else:
  print('No relevant email found')