# Django imports
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# System imports
import logging
import urllib.parse
import json

# local imports 
import sms_app.sms_utilities.messaging as msgutil
from sms_app.models import User
from sms_app.nlp_engine.nlp_manager import NLP_Manager

LOGGER = logging.getLogger('friday_logger')

@csrf_exempt
def receive_msg(request):
    if request.method == 'POST':
        # decode and process request
        sms = msgutil.decode_request(request)
        phone_num = sms['From'][0]
        msg = sms['Body'][0]

        reply = process_msg(msg, phone_num)

    response = json.dumps([{'Success': reply}])

    return HttpResponse(response, content_type='text/json')

@csrf_exempt
def receive_msg_discord(request):
    if request.method == 'POST':
        # decode and process request
        sms = msgutil.decode_request(request)
        name = sms['From'][0]
        msg = sms['Body'][0]

        reply = process_msg_discord(msg, name)
        LOGGER.info('From Stu: %s', reply)

    response = json.dumps([{'Success': reply}])

    return HttpResponse(response, content_type='text/json')

def process_msg_discord(received_msg, name):
    # Find the user
    user = User.find_user_from_name(name)
    response_msgs = list()

    if user is None:
        # Prompt for username
        response_msgs.append(NLP_Manager.get_first_time_greeting_msg())

        # Create a user
        user = User(name=name, state=User.DIS)
        user.save()

        # Create nlp manager
        nlp_manager = NLP_Manager(user)

        LOGGER.info("From %s: %s", user.name, received_msg)

        # Prompt for daily motivation
        msg = nlp_manager._get_onboarding_message()
        LOGGER.info(msg)
        nlp_manager._add_reply_msg(msg)

        response_msgs.append(msg)
        return response_msgs

    else:
        # Create nlp manager
        nlp_manager = NLP_Manager(user)
        LOGGER.info("From %s: %s", user.name, received_msg)

        nlp_manager.process_message(received_msg)
        response_msgs = nlp_manager.get_response()

        return [i[1] for i in response_msgs]
    

def process_msg(received_msg, phone_num):
    # Find the user
    user = User.find_user_from_phone(phone_num)

    # if user can't be found
    if user is None:
        # Prompt for username
        msg = NLP_Manager.get_first_time_greeting_msg()
        send_msg(msg, phone_num)
        msg = NLP_Manager.get_name_prompt_msg()
        send_msg(msg, phone_num)

        # Create temp username with temp ID
        user = User(phone_number=phone_num, state=User.REG)
        user.save()
        return 'Registering phone number, what is your name?'

    # if phone number is found

    # Initiate nlp manager with the user
    nlp_manager = NLP_Manager(user)

    LOGGER.info("From %s: %s", user.name, received_msg)

    nlp_manager.process_message(received_msg)

    reply_queue = nlp_manager.get_response()

    for msg_type, reply in reply_queue:
        if msg_type == NLP_Manager.MESSAGE:
            send_msg(reply, phone_num)
        elif msg_type == NLP_Manager.MEDIA:
            #TODO: send media
            pass
    
    return reply_queue


def send_msg(msg, phone_num):
    LOGGER.info('From Stu: %s', msg)
    #msgutil.send_test_message(msg, phone_num)
    # FIXME: replace with this when done testing
    msgutil.send_message(msg, phone_num)

