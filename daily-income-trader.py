# https://github.com/smkent/waffles/blob/70c9d32522adea456216b5f95e541dd9f092e4ba/wafflesbot/jmap.py#L349-L353

import os

from jmapc import (
    Client,
    Ref,
)

from jmapc.methods import (
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
print(f"Found the mailbox named {mailbox.name} with ID {mailbox.id}")
print(
    f"This mailbox has {mailbox.total_emails} emails, "
    f"{mailbox.unread_emails} of which are unread"
)

# Example output:
#
# Found the mailbox named Inbox with ID deadbeef-0000-0000-0000-000000000001
# This mailbox has 42 emails, 4 of which are unread
