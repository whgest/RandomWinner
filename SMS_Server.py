from twilio.rest import TwilioRestClient
import twilio.twiml
import os

from flask import Flask, request, make_response, session, redirect, url_for

app = Flask(__name__)

app.debug = True
app.secret_key = '3kjbh645ikuh69er8gtyhoi45t98er(^&(*hjkgnvf'

ACCOUNT_SID = "AC73f144c9d7209ff6ebb9de9988512886"
AUTH_TOKEN = "c893ece55d239042f01e4aeca0427cd0"

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
messages = client.messages.list()

entrants_dict = {}

@app.route('/', methods=['GET', 'POST'])
def receive_text():
    try:
        initials = request.values.get('Body', None)[:3].upper()
        if not initials:
            raise TypeError
        entrants_dict[request.values.get('From', None)] = initials
        message = "You've been entered! Initials recieved: %s. If you want to change your initials, just text again." % initials
    except:
        message = "Entry not successful: we need your initials! Please try again."

    resp = twilio.twiml.Response()
    resp.message(message)
    return str(resp)


