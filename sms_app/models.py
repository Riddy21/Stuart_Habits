# django imports
from unicodedata import category
from django.db import models

# system imports 
import uuid
import json
import logging
import time
import datetime

LOGGER = logging.getLogger('friday_logger')

        
class ConvMsg(models.Model):
    """
    Class to save the conversation history of a user
    """
    # FIXME: Change this name according to the app name
    ENGINE = 'Engine'
    MESSAGE = 'Message'
    MEDIA = 'Media'

    # History is list stored as json, default empty list
    message = models.TextField()
    msg_type = models.CharField(max_length=20, default=MESSAGE)
    author = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    conv_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class User(models.Model):
    # FIXME: Add more user states based on the operation being performed
    REG = 'Registration'
    DIS = 'Discussion'

    # Identification info
    name = models.CharField(max_length=50, blank=True)

    phone_number = models.CharField(max_length=12)

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # State of the conversation at that moment
    state = models.CharField(max_length=30, default=REG)

    # Complete conversation history
    conv_history = models.ManyToManyField(ConvMsg, related_name='conversation_history')

    # FIXME: Add more user items to track

    # -----------------------
    # Public Instance Methods
    # -----------------------

    ##############################################
    # For modifying the conversation history stack
    ##############################################
    def add_conversation_msg(self, msg, sender):
        conv = ConvMsg(message=msg, author=sender, phone_number=self.phone_number)
        conv.save()
        self.conv_history.add(conv)
        self.save()

    def add_conversation_media(self, media, sender):
        conv = ConvMsg(message=media,
                       msg_type=ConvMsg.MEDIA,
                       author=sender,
                       phone_number=self.phone_number)
        conv.save()

        self.conv_history.add(conv)
        self.save()

    def get_conversation(self):
        in_conversation_set = set(self.conv_history.all())
        curated_conversation_list = list()

        # Create list for the discussion
        for conv_item in in_conversation_set:
            msg = conv_item.message
            author = conv_item.author
            timestamp = conv_item.timestamp
            curated_conversation_list.append({'Timestamp': timestamp,
                                            'Author': author, 'Message': msg})
        
        # sort the curated discussion list by time
        curated_conversation_list.sort(key=lambda x:x['Timestamp'])

        return curated_conversation_list

    # -----------------------
    # Static Public functions
    # -----------------------

    def find_user_from_phone(phone_num):
        """
        Tries to find using phone num, returns None if not found
        """
        try:
            user = User.objects.get(phone_number=phone_num)
        except:
            return None

        return user

