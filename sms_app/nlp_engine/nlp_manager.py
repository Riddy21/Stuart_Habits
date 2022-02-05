# System imports
import logging
import datetime

# local imports
from sms_app.models import *
import sms_app.gpt3_utilities.response_utilities as gpt3

LOGGER = logging.getLogger('friday_logger')

class NLP_Manager(object):
    MESSAGE = 'Message'
    MEDIA = 'Media'

    def __init__(self, user):
        """Constructor"""
        self.user = user

        self.reply_queue = list()

    # -----------------------
    # Static Public functions
    # -----------------------

    def get_first_time_greeting_msg():
        """Returns greeting for first time users"""
        # FIXME: Add greeting message
        msg = "Hi there!"
        return msg
        
    def get_name_prompt_msg():
        """
        Returns a prompt for the user's name
        """
        msg = "I don\'t recognize this phone number, how should I refer to you?"
        return msg

    # ------------------------------
    # Public Interface for responses
    # ------------------------------
    def process_message(self, received_msg):
        """
        Main function for decifering a response from the user
        """
        # if in registration mode
        if self.user.state == User.REG:
            # Try and find name in response
            name = gpt3.find_name_from_msg(received_msg)

            # if message contains no name reprompt
            # FIXME: Rename to whatever the name of the app is
            if name is None or name == 'Friday':
                msg = self._get_reprompt_for_name()
                self._add_reply_msg(msg)
                return

            # Add name to the user
            self.user.name = name
            # Change to any state, will change after
            self.user.state = User.DIS
            # FIXME: Do all other user settings

            self.user.save()

            msgs = self._get_onboarding_messages()
            for msg in msgs:
                self._add_reply_msg(msg)
            return

        # Add the user msg to conversation hist
        self.user.add_conversation_msg(received_msg, self.user.name)

        # A classification function that determines the user state
        # FIXME: Initiate classifier when more branches come
        #self.user.state = gpt3.determine_conversation_category(received_msg)

        if self.user.state == User.DIS:
            LOGGER.info('You are now in discussion')
            msg = self._get_discussion_response(received_msg)
            self._add_reply_msg(msg)
            return


    def get_response(self):
        """
        Returns the reply_queue
        """
        return self.reply_queue

    # ------------------------
    # Private helper functions
    # ------------------------

    #############################
    # Tools modifying reply_queue
    #############################
    def _add_reply_msg(self, msg):
        """
        Adds reply message to the reply queue
        """
        self.reply_queue.append((self.MESSAGE, msg))
        self.user.add_conversation_msg(msg, ConvMsg.ENGINE)

    def _add_reply_media(self, media):
        """
        Adds reply media to the reply queue
        """
        self.reply_queue.append((self.MEDIA, media))
        # TODO: Don't add this in just yet, the app might not know what to do with it
        # self.user.add_conversation_msg(media, ConvMsg.FRIDAY)

    
    ###################################
    # User State specific functionality
    ###################################

    #-------------
    # Registration
    #-------------

    def _get_reprompt_for_name(self):
        """
        Try to decifer message to find name, if not found return None
        """
        msg = "I'm sorry, I don't think I understood. What would you like me to call you?"
        return msg

    #-----------
    # Onboarding
    #-----------
    def _get_onboarding_messages(self):
        """
        Sends an onboarding message that describes what the API does
        """
        msgs = []
        # FIXME: Change to what is needed with the new app
        msgs.append("How can I help %s?" % self.user.name)
        return msgs

    #-----------
    # Discussion
    #-----------
    def _get_discussion_response(self, msg):
        """
        Sends msg to openAI and get a response back
        """
        # Add user message to discussion hist
        # NOTE: Don't need
        # self.user.add_discussion_msg(msg, self.user.name)
        # Decode discussion history into dictionary list
        conversation_list = self.user.get_conversation()
        # Send past 20 discussion history items to the API
        response_msg = gpt3.get_discussion_response(conversation_list[-20:], self.user.name)
        # Add friday message to discussion hist
        # NOTE: Don't need
        # self.user.add_discussion_msg(response_msg, ConvMsg.FRIDAY)
        return response_msg
