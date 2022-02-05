import os
import openai
import logging
import json
import datetime

from sms_app.models import User

LOGGER = logging.getLogger('friday_logger')

openai.apikey = os.getenv("OPENAI_API_KEY")

################
# Top Classifier
################
def determine_conversation_category(text):
    """
    Takes an input text and categorizes the intent of the query.
    """
    response = openai.Classification.create(
        search_model="davinci",
        model="davinci",
        query=text,
        examples=[
            # FIXME: Change these to examples of the new app that we need 
            # Setup examples
            # Discussion
            ["Tell me about yourself", User.DIS],
            ["What does this app do?", User.DIS],
            ["What are you?", User.DIS],
            ["I love you so much", User.DIS],
            ["How are you doing?", User.DIS],
            ["I need someone to talk to", User.DIS],
            ["Hey so I need some inspiration to start my day", User.DIS],
            ["Do you have any advice for me to improve my spending habits?", User.DIS]
        ],
        # FIXME: Change this to suit the flow of the new app
        labels=[User.DIS]
    )
    
    return response["label"]

#######################
# Name finding function
#######################

def find_name_from_msg(msg):
    """
    Decifer message to find name, if not found return None
    """
    prompt = \
"""
Only return the name from the sentence below, if name not found return None
Also, if the name is Friday, return None
Sentence: I'm Bob
Name: Bob
Sentence: T'is I, Helen Mortimer
Name: Helen
Sentence: Hey, its travis speaking
Name: Travis
Sentence: How are you doing?
Name: None
Sentence: My name is Friday
Name: None
Sentence: bill is my name
Name: Bill
Sentence: Will is too good
Name: None
Sentence: Dollar
Name: Dollar
Sentence: riddy
Name: Riddy
Sentence: hello
Name: Hello
Sentence: %s
Name:
""" % msg

    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=prompt,
        temperature=0,
        max_tokens=10,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop="Sentence:"
    )
    name = response.choices[0].text.strip()
    if name == 'None':
        return None
    return name

#####################
# Discussion function
#####################
def get_discussion_response(conv_history, user):
    """
    Takes a list of dictionaries containing the Author and Msg
    in order and generates a response
    """

    # Create a String prompt
    # FIXME: Add prompt for what the app should be like
    prompt = 'Be a friendly chatbot'

    # Populate with conversation
    for message in conv_history:
        prompt += '%s:%s\n' % (message['Author'], message['Message'])

    # FIXME:: Change this to the name of the engine
    prompt += 'Engine:'

    # Send to API
    response_dict = openai.Completion.create(
        engine="text-davinci-001",
        prompt=prompt,
        temperature=1.0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=2.0,
        presence_penalty=2.0,
        stop="%s:" % user
    )

    # Clip any enters off the ends of the string
    response = response_dict['choices'][0]['text'].strip()

    return response

