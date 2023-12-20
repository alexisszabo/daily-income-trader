# https://github.com/smkent/waffles/blob/70c9d32522adea456216b5f95e541dd9f092e4ba/wafflesbot/jmap.py#L349-L353

from datetime import datetime

from jmapc import (
    Client,
    Mailbox,
    Ref,
)

from jmapc.methods import (
    EmailGet,
    EmailGetResponse,
    EmailQuery,
    MailboxGet,
    MailboxGetResponse,
    MailboxQuery,
)

from jmapc.models import (
    EmailQueryFilterCondition,
    MailboxQueryFilterCondition,
)

def get_mail_client(host: str, api_token: str) -> Client:
  return Client.create_with_api_token(host=host, api_token=api_token)

def get_mailbox(client: Client, name: str) -> Mailbox:
  methods = [
      MailboxQuery(filter=MailboxQueryFilterCondition(name=name)),
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
  return mailboxes[0]

def get_emails_after(client: Client, mailbox: str, date: datetime) -> EmailGetResponse:
  # Only check for todays emails
  # Get the email
  methods = [
    EmailQuery(
      filter=EmailQueryFilterCondition(
        in_mailbox=mailbox.id,
        after=date.replace(hour=0, minute=0, second=0)
      )
    ),
    EmailGet(
      ids=Ref("/ids"),
      fetch_all_body_values=True
    )
  ]
  results = client.request(methods)
  assert isinstance(results[1].response, EmailGetResponse)
  return results[1].response.data
