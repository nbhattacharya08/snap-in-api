# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = "AC2deea27febf4d49d44979e23c46aad2c"
auth_token = "fe472d53fb4ae0b7b0d7b29612a986dc"
client = Client(account_sid, auth_token)

call = client.calls.create(
  url="http://demo.twilio.com/docs/voice.xml",
  to="+918981829798",
  from_="+12564856295"
)
print(call.sid)