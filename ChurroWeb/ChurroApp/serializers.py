from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class HouseSerializer(serializers.ModelSerializer):
    name = serializers.JSONField()
    class Meta:
        model = House
        fields = ('pk','name', 'joined')

class ChoreSerializer(serializers.ModelSerializer):
    name = serializers.JSONField()
    date = serializers.DateField()
    # frequency = serializers.JSONField()
    # FreqFields = (
    #     ('DAILY', 'Daily'),
    #     ('WEEKLY', 'Weekly'),
    #     ('FORTNIGHTLY', 'Fortnightly'),
    #     ('MONTHLY', 'Monthly'),
    #     ('QUARTERLY', 'Quarterly'),
    #     ('YEARLY', 'Yearly'),
    #     ('ONCEOFF', 'Once Off')
    # )
    # frequency = serializers.ChoiceField(choices=FreqFields)
    class Meta:
        model = Chore
        fields = ('user_id', 'name', 'date', 'frequency', 'status')

class BillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bill
        fields = ('name', 'due_date', 'frequency', 'total_amount', 'bill_split', 'status')

class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shared_Item
        fields = ('user_id', 'name', 'last_restock', 'done', 'status')

class ReminderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reminder
        fields = ('name', 'time', 'date', 'alert', 'frequency', 'status')

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class FullHouseSerializer(serializers.Serializer):
    house = HouseSerializer(many = False)
    users = UserSerializer(many = True)
    chores = ChoreSerializer(many = True)
    bills = BillSerializer(many = True)
    items = ItemSerializer(many = True)
    reminders = ReminderSerializer(many = True)
