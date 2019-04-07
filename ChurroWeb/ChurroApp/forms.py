from django import forms
from django.db import models
from .models import Chore,House,Shared_Item
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Submit,Fieldset,ButtonHolder
from crispy_forms.bootstrap import (PrependedText, PrependedAppendedText, FormActions)
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from ChurroApp.models import FreqFields, Status_Choice

class ChoreForm(forms.Form):
    chore_name = forms.CharField(label="Name",required=True, max_length = 16)
    chore_date = forms.DateField(label="Due Date",widget=forms.TextInput(attrs={'type':'date'}),required=True)
    chore_status = forms.BooleanField(label="Completed?",required=False)
    chore_frequency = forms.ChoiceField(label = "Frequency",choices=FreqFields)
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        'chore_name',
        'chore_date',
        'chore_frequency',
        'chore_status',
        FormActions(Submit('Save','Save', css_class='btn-primary'))
    )

class HouseForm(forms.Form):
    house_name = forms.CharField(label="Name",required=True, max_length = 16)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        'house_name',
        FormActions(Submit('Save','Save', css_class='btn-primary'))

    )

class HouseJoinForm(forms.Form):
	house_code = forms.CharField(label="Code", required=True, max_length = 8)

	helper = FormHelper()
	helper.form_method = 'POST'
	helper.layout = Layout(
		'house_code',
		FormActions(Submit('Save','Save', css_class='btn-primary'))
	)

class BillForm(forms.Form):
    bill_name = forms.CharField(label="Name",required=True, max_length = 16)
    bill_date = forms.DateField(label="Due Date",widget=forms.TextInput(attrs={'type':'date'}),required=True)
    bill_status = forms.BooleanField(label="Paid",required=False)
    bill_frequency = forms.ChoiceField(label = "Frequency",choices=FreqFields)
    bill_amount = forms.DecimalField(label = "Total Amount",max_digits=10, decimal_places=2)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        'bill_name',
        'bill_date',
        'bill_frequency',
        'bill_amount',
        'bill_status',
        FormActions(Submit('Save','Save', css_class='btn-primary'))
    )

class ItemForm(forms.Form):
    item_name = forms.CharField(label = "Item", required = True, max_length= 16)
    item_status = forms.ChoiceField(label = "Status", choices=Status_Choice)
    item_LastRestock = forms.DateField(label = "Last Restocked",widget=forms.TextInput(attrs={'type':'date'}),required=True)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
    'item_name',
    'item_status',
    'item_LastRestock',
    FormActions(Submit('Save','Save', css_class='btn-primary'))
    )

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class ReminderForm(forms.Form):
    reminder_name = forms.CharField(label="Name",required=True, max_length = 16)
    reminder_time = forms.TimeField(label="Due Time",widget=forms.TextInput(attrs={'type':'time'}),required=True)
    reminder_date = forms.DateField(label="Due Date",widget=forms.TextInput(attrs={'type':'date'}),required=True)
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        'reminder_name',
        'reminder_time',
        'reminder_date',
        FormActions(Submit('Save','Save', css_class='btn-primary'))
    )
class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
			'password'

        )
