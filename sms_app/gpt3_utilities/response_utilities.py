from datetime import date
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
            ["How am I doing on my habits?", User.DIS],
            ["I need someone to talk to", User.DIS],
            ["Hey so I need some inspiration to start my day", User.DIS],
            ["Do you have any advice for me to improve my sleeping habits?", User.DIS],

            # Habit breakdown
            ["Give me a breakdown of my habits", User.BRE],
            ["Provide me with a breakdown of my habits", User.BRE],
            # FIXME: Add more examples
        ],
        # FIXME: Change this to suit the flow of the new app
        labels=[User.DIS, User.BRE]
    )
    
    return response["label"]

def determine_conversation_category_dumb(text):
    """
    Dumb way of determining if in breakdown
    """

    if 'breakdown' in text.lower():
        return User.BRE
    else:
        return User.DIS

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
Also, if the name is Stu, return None
Sentence: I'm Ridguy
Name: Ridguy
Sentence: T'is I, Helen Mortimer
Name: Helen
Sentence: Hey, its travis speaking
Name: Travis
Sentence: How are you doing?
Name: None
Sentence: My name is Stu
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

####################
# Daily greeting functions
####################
def get_daily_greeting_response(user):
    """
    Gets the daily response from gpt3
    """

    prompt = \
"""
The following is a motivational message from the AI assistant accountability partner named Stu to the user %s.

Here are %s's habits and the breakdown of their achievements:
Habit: Go for a run every morning | Running Streak: 16 | Days Missed: 8 | Days Succeeded: 18 | Total days: 26
Habit: Do 30 minutes of meditation every evening | Meditation Streak: 6 | Days Missed: 24 | Days Succeeded: 14 | Total days: 38
Habit: Read a book for one hour a day | Reading Streak: 24 | Days Missed: 2 | Days Succeeded: 29 | Total days: 31

Send %s greeting for the day and give him motivation to accomplish one of the specific goals he has listed above in a sms text message
Stu:Hey %s, I hope you have a great day! I know you can achieve your goal of running every day this streak. Just think about how good you'll feel when you reach your goal!
Stu:
""" % (user, user, user, user)
    
    response_dict = openai.Completion.create(
        engine="text-davinci-001",
        prompt=prompt,
        temperature=0.7,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["Stu"]
    )

    response = response_dict['choices'][0]['text'].strip().replace("\n", " ")

    return response
    
#####################
# Discussion function
#####################
def get_discussion_response(conv_history, user):
    """
    Takes a list of dictionaries containing the Author and Msg
    in order and generates a response
    """

    # Create a String prompt
    prompt = \
"""
The following is a conversation with an AI assistant accountability partner named Stu and the user %s. 
The AI assistant is compassionate, motivational, reflective, inspiring and very friendly. 
The AI assistant will focus on topics relating to self-help, healthy living, mental wellbeing, personal development, and habit building. 
The purpose of the AI assistant is to help %s build habits and meet their personal goals. 
The AI assistant should provide encouraging tips to meet their goals and new ideas to take care of their physical and mental health. 
Stu should answer in a short text about a sentence long. 
Stu must be able to inform %s about everything she can help with. 
Use the book "Atomic Habits" by James Clear as a guideline to answer questions.
Use the book "The Power of Habit" by Charles Duhigg as a guideline to answer questions.
AI assistant has the functionality to help %s with these actions: 
- track habits 
- Give reports on habits
- provide tips on mental health
- provide motivation
- have helpful discussions about goal setting and habit building

Give %s a reward of 20 percent off coupon at Lululemon when they complete their habit 10 times and meet their habit goal.

Here are %s's habits and the breakdown of their achievements:
Habit: Go for a run every morning | Running Streak: 16 | Days Missed: 8 | Days Succeeded: 18 | Total days: 26
Habit: Do 30 minutes of meditation every evening | Meditation Streak: 6 | Days Missed: 24 | Days Succeeded: 14 | Total days: 38
Habit: Read a book for one hour a day | Reading Streak: 24 | Days Missed: 2 | Days Succeeded: 29 | Total days: 31
""" % (user, user, user, user, user, user)

    # Populate with conversation
    for message in conv_history:
        prompt += '%s:%s\n' % (message['Author'], message['Message'])

    # Change this to the name of the engine
    prompt += 'Stu:'

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

#############################
# Habit Break Down functions
#############################

def get_habit_breakdown():
    breakdown = \
"""
Habit: Go for a run every morning | Streak: 16 | Days Missed: 8 | Days Succeeded: 18 | Total days: 26
Habit: Do 30 minutes of meditation every evening | Streak: 6 | Days Missed: 24 | Days Succeeded: 14 | Total days: 38
Habit: Read a book for one hour a day | Streak: 24 | Days Missed: 2 | Days Succeeded: 29 | Total days: 31
Habit: Workout everyday | Streak: 5 | Days Missed: 2 | Days Succeeded: 29 | Total days: 31
"""
    return breakdown







