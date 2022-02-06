# django imports
from re import I
from unicodedata import category
from django.db import models

# system imports 
import uuid
import json
import logging
import time
import datetime

LOGGER = logging.getLogger('friday_logger')

class Achievement(models.Model):
    """
    Class to save an achievement
    """
    category = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    achievement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def make_achievement(habit_name, timestamp):
        if timestamp == '?':
            timestamp = datetime.datetime.now()
        else:
            try:
                date = datetime.datetime.strptime(timestamp, '%m-%d-%Y')
                if date.date() == datetime.date.today():
                    timestamp = datetime.datetime.now()
                else:
                    timestamp = datetime.datetime(date.year, date.month, date.day)
            except:
                LOGGER.error('Date not recorded properly')    
        
        achievement = Achievement(category=habit_name,
                                  timestamp=timestamp)
        achievement.save()
        return achievement

class Habit(models.Model):
    """
    Class to save a habit
    """
    name = models.CharField(max_length=100)
    # Period is an integer of how many days per achievement
    period = models.IntegerField()
    start_date = models.DateTimeField(auto_now_add=True, editable=False)
    habit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def make_habit(name, period=1):
        """
        First time creation of a habit, makes the habit making easier if the user doesn't specify a period
        """
        habit = Habit(name=name,
                      period=period)
        habit.save()
        return habit

        
class ConvMsg(models.Model):
    """
    Class to save the conversation history of a user
    """
    # FIXME: Change this name according to the app name
    ENGINE = 'Stu'
    MESSAGE = 'Message'
    MEDIA = 'Media'

    # History is list stored as json, default empty list
    message = models.TextField()
    msg_type = models.CharField(max_length=20, default=MESSAGE)
    author = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    conv_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class User(models.Model):
    # FIXME: Add more user states based on the operation being performed
    REG = 'Registration'
    DIS = 'Discussion'
    #TRA = 'Track achievement'
    #MOD = 'Habit modification'
    BRE = 'Breakdown'
    DAY = 'Start of day message'

    # Identification info
    name = models.CharField(max_length=50, blank=True)

    phone_number = models.CharField(max_length=12, blank=True)

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # State of the conversation at that moment
    state = models.CharField(max_length=30, default=REG)

    # Complete conversation history
    conv_history = models.ManyToManyField(ConvMsg, related_name='conversation_history')

    # Habits the user has
    habits = models.ManyToManyField(Habit, related_name='habits_collection')

    # Acheivements the user has
    achievements = models.ManyToManyField(Achievement, related_name='achievement_history')

    # -----------------------
    # Public Instance Methods
    # -----------------------

    ##############################################
    # For modifying the conversation history stack
    ##############################################
    def add_conversation_msg(self, msg, sender):
        conv = ConvMsg(message=msg, author=sender)
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

    #############################
    # Habit information functions
    #############################
    def get_habit_names_list(self):
        habits = set(self.habits.all())
        out_habits_list = list()

        for habit in habits:
            out_habits_list.append(habit.name)

        return out_habits_list
    
    def get_habit_from_name(self, name):
        habits = set(self.habits.all())
        for habit in habits:
            if name == habit.name:
                return habit
        return False

    def modify_habits_from_dict(self, habits_dict):
        habit_list = list()

        for name, period in habits_dict.items():
            # if the habit already exists then transfer it over
            habit = self.get_habit_from_name(name)
            if habit:
                habit_list.append(habit)
                continue

            # make new habit
            if period == '?':
                habit = Habit.make_habit(name)
            else:
                try:
                    period = int(period)
                except:
                    LOGGER.error('not a valid period for habit creation')
                    continue

                habit = Habit.make_habit(name, period)

            habit_list.append(habit)

        # Delete all previous categories
        for habit in self.habits.all():
            habit.delete()
        self.habits.clear()

        # Add the new ones in
        for habit in habit_list:
            self.habits.add(habit)
            self.save()

    ###################################
    # Achievement infmoration functions
    ###################################
    def add_achievement(self, habit_name, timestamp):
        # Check if the habit is in the list of habits
        if habit_name not in self.get_habit_names_list:
            LOGGER.info('Error: the habit could not be found')
            return
        
        # make the achievement
        achievement = Achievement.make_achievement(habit_name, timestamp)
        self.achievements.add(achievement)
        self.save()

    def get_acheivements(self, habit_name):
        if habit_name not in self.get_habit_names_list:
            LOGGER.error('Error: the habit could not be found')
            return

        # Find all acheivements under that category
        achievement_list = list()

        achievement_query_set = self.achievements.all()

        for achievement in achievement_query_set:
            date = achievement.timestamp
            achievement_habit = achievement.category
            # TODO: Only add if the date is before the habit start
            pass

    ###############
    # For DEMO ONLY
    ###############
    def setup_demo_presets(self):
        """
        Set up a bunch of habits and acheivements by default just so it has some infomration to work with
        """
        pass

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

    def find_user_from_name(name):
        """
        Tries to find using name, returns None if not found
        """
        try:
            user = User.objects.get(name=name)
        except:
            return None

        return user

