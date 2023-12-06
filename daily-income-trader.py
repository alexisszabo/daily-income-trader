# https://github.com/smkent/waffles/blob/70c9d32522adea456216b5f95e541dd9f092e4ba/wafflesbot/jmap.py#L349-L353

import os
import re
from datetime import datetime
from jmapc import (
    Client,
    Ref,
)

from jmapc.methods import (
    EmailGet,
    EmailGetResponse,
    EmailQuery,
    MailboxChanges,
    MailboxChangesResponse,
    MailboxGet,
    MailboxGetResponse,
    MailboxQuery,
    MailboxQueryChanges,
    MailboxQueryChangesResponse,
    MailboxQueryResponse,
    MailboxSet,
    MailboxSetResponse,
)
from jmapc.models import (
    EmailQueryFilterCondition,
    MailboxQueryFilterCondition,
)

client = Client.create_with_api_token(
    host=os.environ["JMAP_HOST"], api_token=os.environ["JMAP_API_TOKEN_DIT"]
)

methods = [
    MailboxQuery(filter=MailboxQueryFilterCondition(name=os.environ["JMAP_FOLDER_NAME_DIT"])),
    MailboxGet(ids=Ref("/ids")),
]

# Call JMAP API with the prepared request
results = client.request(methods)

# Retrieve the InvocationResponse for the second method. The InvocationResponse
# contains the client-provided method ID, and the result data model.
method_2_result = results[1]

# Retrieve the result data model from the InvocationResponse instance
method_2_result_data = method_2_result.response

# Retrieve the Mailbox data from the result data model
assert isinstance(
    method_2_result_data, MailboxGetResponse
), "Error in Mailbox/get method"
mailboxes = method_2_result_data.data

# Although multiple mailboxes may be present in the results, we only expect a
# single match for our query. Retrieve the first Mailbox from the list.
mailbox = mailboxes[0]

# Print some information about the mailbox
#print(f"Found the mailbox named {mailbox.name} with ID {mailbox.id}")
#print(
#    f"This mailbox has {mailbox.total_emails} emails, "
#    f"{mailbox.unread_emails} of which are unread"
#)

# Only check for todays emails
after = datetime.today().replace(hour=0, minute=0, second=0);

# Get the email
methods = [
  EmailQuery(
    filter=EmailQueryFilterCondition(
      in_mailbox=mailbox.id,
      after=after,
    )
  ),
  EmailGet(
    ids=Ref("/ids"),
    fetch_all_body_values=True
  )
]
results = client.request(methods)
assert isinstance(results[1].response, EmailGetResponse)
emails = results[1].response
n_emails = len(emails.data)

if (n_emails == 1):
  email = emails.data[0]
  text_body = email.body_values['1'].value

  ticker = ''
  signal_price = 0.0 
  target_price = 0.0
  stop_loss_price = 0.0 

  for line in text_body.splitlines():
    match = re.search('Today’s Daily Market Profit Alerts is \\$([A-z]+)', line) 
    if match:
      ticker = match.group(1)

    match = re.search('^Signal Price: \\$([0-9.])', line)
    if match:
      signal_price = float(match.group(1))

    match = re.search('^Target Price: \\$([0-9.])', line)
    if match:
      target_price = float(match.group(1))

    match = re.search('^Stop Loss Price: \\$([0-9.])', line)
    if match:
      stop_loss_price = float(match.group(1))

  if ticker != '' and signal_price > 0 and target_price > 0 and stop_loss_price > 0:
    print("Parsed Today's Daily Profits Alert Email")
    print(f"Ticker: ${ticker}")
    print(f"Signal Price: ${signal_price}")
    print(f"Target Price: ${target_price}")
    print(f"Stop Loss Price: ${stop_loss_price}")

elif (n_emails > 0):
  print('Found more emails than expected')
else:
  print('No relevant email found')

# Example output:
#
# Found the mailbox named Inbox with ID deadbeef-0000-0000-0000-000000000001
# This mailbox has 42 emails, 4 of which are unread
