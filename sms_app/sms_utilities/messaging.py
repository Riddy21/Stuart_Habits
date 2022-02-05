# twilio imports
from twilio.rest import Client

# System imports
import urllib.parse
import os
import logging

# local imports

# Twillio setup
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

LOGGER = logging.getLogger('friday_logger')

def decode_request(request):
    """
    Decodes the POST request from the app
    """
    return urllib.parse.parse_qs(request.body.decode('utf-8'))

def send_test_message(msg, phone_num):
    """
    Testing send mess function
    """
    LOGGER.info('From Engine: %s', msg)

def send_message(msg, phone_num):
    """
    Constructs a response message json for API to send back
    """
    response = TWILIO_CLIENT.messages.create(
            body=msg,
            to=phone_num,
            media_url=None,
            from_=TWILIO_NUMBER
            )
