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
        msg = ("Hi there! I'm Stuart, but call me Stu. "
              "I'm your wellness buddy who's focused on helping you build healthier habits "
              "and take care of your mental health.")
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
            if name is None or name == 'Stu':
                msg = self._get_reprompt_for_name()
                self._add_reply_msg(msg)
                return
            
            # Try and find the user first
            user = User.find_user_from_name(name)
            if user is None:
                # Add name to the user
                self.user.name = name
                # Change to any state, will change after
                self.user.state = User.DIS
                # FIXME: Do all other user settings

                self.user.save()

                msg = self._get_onboarding_message()
                self._add_reply_msg(msg)
                return
            else:
                # Delete the temp user and add phone number to this user
                user.phone_number = self.user.phone_number
                self.user.delete()
                self.user = user
                self.user.state = User.DIS
                self.user.save()

                msg = self._get_onboarding_message()
                self._add_reply_msg(msg)
                return

        # Add the user msg to conversation hist
        self.user.add_conversation_msg(received_msg, self.user.name)

        # A classification function that determines the user state
        # FIXME: Initiate classifier when more branches come
        #self.user.state = gpt3.determine_conversation_category(received_msg)
        self.user.state = gpt3.determine_conversation_category_dumb(received_msg)

        if self.user.state == User.DIS:
            LOGGER.info('You are now in discussion')
            #FIXME: Reenable for testing 
            msg = self._get_discussion_response(received_msg)
            #msg = "AI Disabled, This is a test reply"
            self._add_reply_msg(msg)
            return

        #elif self.user.state == User.TRA:
        #    LOGGER.info('You are now in habit tracking')
        #    #msg = self._get_discussion_response(received_msg)
        #    # FIXME route to extract_habit_info function
        #    #self._add_reply_msg(msg)
        #    return
        
        #elif self.user.state == User.MOD:
        #    LOGGER.info('You are now in habit modification')
        #    #msg = self._get_discussion_response(received_msg)
        #    # FIXME route to modify habit function
        #    #self._add_reply_msg(msg)
        #    return
        
        #elif self.user.state == User.FED:
        #    LOGGER.info('You are now in feedback')
        #    #msg = self._get_discussion_response(received_msg)
        #    # FIXME route to habit feedback function
        #    #self._add_reply_msg(msg)
        #    return
        
        elif self.user.state == User.BRE:
            LOGGER.info('You are now in habit breakdown')
            msg = self._get_breakdown_response(received_msg)
            # FIXME route to habit breakdown function
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

    # NOTE: No need for media right now
    #def _add_reply_media(self, media):
    #    """
    #    Adds reply media to the reply queue
    #    """
    #    self.reply_queue.append((self.MEDIA, media))
    #    # Don't add this in just yet, the app might not know what to do with it
    #    # self.user.add_conversation_msg(media, ConvMsg.FRIDAY)

    
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
    def _get_onboarding_message(self):
        """
        Sends an onboarding message that describes what the API does
        """
        # FIXME: Change to what is needed with the new app
        msg = gpt3.get_daily_greeting_response(self.user.name)
        return msg

    #-----------
    # Discussion
    #-----------
    def _get_discussion_response(self, msg):
        """
        Sends msg to openAI and get a response back
        """
        # Add user message to discussion hist
        # Decode discussion history into dictionary list
        conversation_list = self.user.get_conversation()
        # Send past 20 discussion history items to the API
        response_msg = gpt3.get_discussion_response(conversation_list[-20:], self.user.name)
        # Add friday message to discussion hist
        return response_msg

    def _get_breakdown_response(self, msg):
        """
        Send msg to openAI and get a response back
        """
        response_msg = gpt3.get_habit_breakdown()

        return response_msg

