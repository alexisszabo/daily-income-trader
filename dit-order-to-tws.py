# 1. Read order from database (only those that match the current day, and are not yet submitted)
# 2. For each order:
#   a. Query Account to get balance
#   b. Calculate sizes (if balance available)
#   c. Place Order
from db.models import Order as OrderDb
import datetime as dt
from ib_insync import *
import math
import os
from signal import signal, SIGINT
from sys import exit
import time
from decimal import Decimal

is_paper_trading = True
max_loss_per_trade_in_percent = 2
HOST_IP="127.0.0.1"
ib = IB()

def main():
  ib.errorEvent += on_error
  ib.disconnectedEvent += on_disconnected
  ib.timeoutEvent += on_timeout
  if is_paper_trading:
    port = 7497
    account_name = os.environ["TWS_PAPER_ACCOUNT_NAME_DIT"]
  else:
    raise Exception("you're not ready for the real account yet!")
    port = 7496
    account_name = os.environ["TWS_LIVE_ACCOUNT_NAME_DIT"]

  while True:
    connect_if_needed(port)
    if ib.isConnected():
      submit_pending_orders(account_name)
    time.sleep(10)

def connect_if_needed(port):
  if not ib.isConnected():
    ib.disconnect()
    try:
      ib.connect(HOST_IP, port, clientId=1)
      print("Connected!")
    except OSError:
      print("Connection Failed. Will Retry.")

def submit_pending_orders(account_name):
  # Retrieve Orders from Database
  today = dt.datetime.today()
  orders_to_process = OrderDb.objects.filter(date=today, is_processed=False)
  if orders_to_process.count() < 1:
    return 

  for order_db in orders_to_process:
    # Retrieve balances from account
    account_values = ib.accountValues(account_name)
    # Net Liquidation is the total value of the account, including unsettled trades
    net_liquidation = Decimal(get_value_from_account_value(account_values, 'NetLiquidationByCurrency', 'USD'))
    # Cash balance is the actual cash available in the account for buying
    cash_balance = Decimal(get_value_from_account_value(account_values, "CashBalance", "USD"))

    # Calculate size
    # This is based on the max loss of the account (based on net liquidation)
    stop_loss_amount = order_db.signal_price - order_db.stop_loss_price
    max_loss = net_liquidation * max_loss_per_trade_in_percent / 100
    size = int(math.floor(max_loss / stop_loss_amount))
    
    # If the amount of available cash is not enough for the size, make the size smaller (based on cash balance)
    # Technically I should be using the limit_price, but since this is a margin account, the discreplancy should be fine.
    if (size * order_db.signal_price) > cash_balance:
      size = int(math.floor(cash_balance / order.signal_price))

    contract = Stock(order_db.ticker,'SMART','USD')

    # Don't submit the order if the current price exceeds the signal price.
    # This avoids submitting an order on a stock that already run and could be on it's way down now
    ticker = get_ticker(contract)
    if (ticker.ask > order_db.signal_price):
      print_new_section()
      print(f"Skipping {order_db.ticker} as current price exceeds the signal price")
      order_db.is_processed = True
      order_db.save()
      continue

    #######################
    ##### Place Order #####
    #######################

    # Allow for some slippage for the case of fast-moving stocks
    buy_limit_price = to_currency(order_db.signal_price * 1.02)

    # Generate Order
    stop_limit_order = StopLimitOrder(
      'BUY', size, buy_limit_price, order_db.signal_price,
      orderId=ib.client.getReqId(),
      transmit=False
      ) 
    take_profit_order = LimitOrder(
      'SELL', size, order_db.target_price,
      orderId=ib.client.getReqId(),
      parentId=stop_limit_order.orderId,
      usePriceMgmtAlgo=False,
      transmit=False,
      )
    stop_loss_order = StopOrder(
      'SELL', size, order_db.stop_loss_price,
      orderId=ib.client.getReqId(),
      parentId=stop_limit_order.orderId,
      transmit=False
      )
    time_to_sell = f"{dt.datetime.today().strftime("%Y%m%d")} 15:50:00 US/Eastern"
    sell_at_end_of_day_order = MarketOrder(
      'SELL', size,
       conditions = [TimeCondition(isMore=True, time=time_to_sell)],
       orderId=ib.client.getReqId(),
       parentId=stop_limit_order.orderId,
       transmit=True
    )

    print_new_section()
    print(f"Placing {order_db.ticker} Orders")
    for order in [stop_limit_order, take_profit_order, stop_loss_order, sell_at_end_of_day_order]:
      print(order)
      ib.placeOrder(contract, order)
    order_db.is_processed = True
    order_db.is_submitted = True
    order_db.save()

def to_currency(amount: float) -> Decimal:
  return int(Decimal(amount)*100)/100

def get_value_from_account_value(account_values: AccountValue, name, currency='USD'):
  for account_value in account_values:
    if account_value.tag == name and account_value.currency == currency:
      return account_value.value
  return None

def get_ticker(contract: Stock, genericTickList="") -> Ticker:
  ticker = ib.reqMktData(contract, genericTickList, snapshot=True)
  while math.isnan(ticker.ask):
    ib.sleep(0.1)
  return ticker

def print_new_section():
  print("------------------------")
  print(dt.datetime.now()) 

def handler(signal_received, frame):
  # Handle any cleanup here
  print_new_section()
  print('Disconnecting from TWS...')
  ib.disconnect()
  exit(0)

def on_error(self, reqId, errorCode, errorString):
  print_new_section()
  print(f"reqId: {reqId}")
  print(f"errorCode: {errorCode}")
  print(f"erroString: {errorString}")

def on_disconnected():
  print_new_section()
  print("Disconnected!")

def on_timeout(idlePeriod: float):
  print_new_section()
  print("Timeout!")

if __name__ == "__main__":
  signal(SIGINT, handler)
  main()
