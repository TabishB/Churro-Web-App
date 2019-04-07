from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .forms import *
from .models import Chore, House, Bill, Shared_Item, Profile,Reminder
from django.http import HttpResponse
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import date, timedelta
import datetime
from random import randint
import string
import json

from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout

from collections import namedtuple
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from .serializers import *
from django.db.models import Q


def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def landing(request):
    return  render(request, 'ChurroApp/landing.html')

def logout_view(request):
    logout(request)

def logoutsuccess(request):
    return render(request, 'ChurroApp/landing.html')

def loginfailure(request):
    return  render(request, 'ChurroApp/loginfailure.html')

def account(request):
    args = {'user': request.user}
    return  render(request, 'ChurroApp/account.html', args)

@login_required
def edit_account(request):
    if request.method == 'POST':
        print('save 1')
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            print('save worked')
            return redirect('account')
    else:
        print('save 2')
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'ChurroApp/edit_account.html', args)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'ChurroApp/signup.html', {'form': form})

def houseerror(request):
    return render(request, 'ChurroApp/houseerror.html')

@login_required()
def dashboard(request):
    if checkHouse(request):
        return redirect('house_error')
    # filters users to find the current user and finds them in profiles, and gets their respective house
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    house = getHouse(request)
    now = timezone.now()
    reminder_time = Reminder.objects.values('name', 'time').filter(house_id = house, date = datetime.datetime.today()).order_by('time')
    time = []
    for entry in reminder_time:
        time.append(entry['time'].strftime("%H:%M"))

    reminders = Reminder.objects.filter(house_id=house).order_by('date')
    items = Shared_Item.objects.filter(house_id=house).exclude(status='High').order_by('status')
    bills = Bill.objects.filter(house_id=house,due_date__lte= (datetime.date.today()+timedelta(days=7)),status=0).order_by('due_date')
    chores = Chore.objects.filter(house_id=house,date__gte = datetime.date.today(),date__lte= (datetime.date.today()+timedelta(days=7)),status=0).order_by('date')
    return render(request, 'ChurroApp/dashboard.html',{'items':items,'bills':bills,'chores':chores,'reminders':reminders, 'profiles':profiles,'reminder_times':time})

# depending on button clicked returns the total amount for the house for each bill
# or split amount of the bill for the house
def get_data(house, month, clicked):
    numMonth = datetime.datetime.strptime(month, '%B').month

    data = []
    if clicked:
        dataset = Bill.objects \
        .values('name', 'bill_split') \
        .filter(house_id = house, due_date__month=numMonth) \
        .order_by('-bill_split')

        for entry in dataset:
            name = entry['name']
            amount = float(entry['bill_split'])
            data.append([name, amount])
    else:
        dataset = Bill.objects \
        .values('name', 'total_amount') \
        .filter(house_id = house, due_date__month=numMonth) \
        .order_by('-total_amount')

        for entry in dataset:
            name = entry['name']
            amount = float(entry['total_amount'])
            data.append([name, amount])

    return data

def chart_data(request):
    house = getHouse(request)

    dataset = {}
    # x axis values for year view
    keys = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December']

    result = dict((m, 0) for m in keys)

    clicked = False

    title = ''

   # if my bill share button clicked, displays the bill split total for each month
   # otherwise it displays the total bill amount for the house
    if request.GET.get('clicked') == 'true':
        clicked = True
        dataset = Bill.objects \
        .values('bill_split', 'due_date') \
        .filter(house_id = house, due_date__year=datetime.date.today().year)\
        .order_by('due_date')

        for i in dataset:
            month = str(i.get('due_date').strftime("%B"))
            result[month] = result[month] + float(i.get('bill_split'))

        title = 'My Utility Expenses Share'
    else:
        dataset = Bill.objects \
        .values('total_amount', 'due_date') \
        .filter(house_id = house, due_date__year=datetime.date.today().year)\
        .order_by('due_date')

        for i in dataset:
            month = str(i.get('due_date').strftime("%B"))
            result[month] = result[month] + float(i.get('total_amount'))

        title = 'Total Utility Expenses For House'

    chart = {
        'chart': {'type': 'column'},
        'title': {'text': title},
        'subtitle': {'text': 'Click the columns to view monthly expenses.'},
        'xAxis': {'type': 'category'},
        'yAxis': {
            'title': {'text': 'Total expense ($)'}
        },
        'legend': {'enabled': 'false'},
        'plotOptions': {
            'series': {
                'borderWidth': 0,
            }
        },
        'tooltip': {
            'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
            'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>${point.y:.2f}</b><br/>'
        },

        "series": [{
            "name": "Year view",
            "colorByPoint": 'true',
            "data": [
                {
                    "name": "January",
                    "y": result['January'],
                    "drilldown": "January"
                },
                {
                    "name": "February",
                    "y": result['February'],
                    "drilldown": "February"
                },
                {
                    "name": "March",
                    "y": result['March'],
                    "drilldown": "March"
                },
                {
                    "name": "April",
                    "y": result['April'],
                    "drilldown": "April"
                },
                {
                    "name": "May",
                     "y": result['May'],
                    "drilldown": "May"
                },
                {
                    "name": "June",
                    "y": result['June'],
                    "drilldown": "June"
                },
                {
                    "name": "July",
                    "y": result['July'],
                    "drilldown": 'July'
                },
                {
                    "name": "August",
                    "y": result['August'],
                    "drilldown": 'August'
                },
                {
                    "name": "September",
                    "y": result['September'],
                    "drilldown": 'September'
                },
                {
                    "name": "October",
                    "y": result['October'],
                    "drilldown": 'October'
                },
                {
                    "name": "November",
                    "y": result['November'],
                    "drilldown": 'November'
                },
                {
                    "name": "December",
                    "y": result['December'],
                    "drilldown": 'December'
                }
            ]
        }],
        "drilldown": {
            "series": [
                {
                    "name": "January",
                    "id": "January",
                    'data': get_data(house, "January", clicked)
                },
                {
                    "name": "February",
                    "id": "February",
                    'data': get_data(house, "February", clicked)
                },
                {
                    "name": "March",
                    "id": "March",
                    'data': get_data(house, "March", clicked)
                },
                {
                    "name": "April",
                    "id": "April",
                    'data': get_data(house, "April", clicked)
                },
                {
                    "name": "May",
                    "id": "May",
                    'data': get_data(house, "May", clicked)
                },
                {
                    "name": "June",
                    "id": "June",
                    'data': get_data(house, "June", clicked)
                },
                {
                    "name": "July",
                    "id": "July",
                    'data': get_data(house, "July", clicked)
                },
                {
                    "name": "August",
                    "id": "August",
                    'data': get_data(house, "August", clicked)
                },
                {
                    "name": "September",
                    "id": "September",
                    'data': get_data(house, "September", clicked)
                },
                {
                    "name": "October",
                    "id": "October",
                    'data': get_data(house, "October", clicked)
                },
                {
                    "name": "November",
                    "id": "November",
                    'data': get_data(house, "November", clicked)
                },
                {
                    "name": "December",
                    "id": "December",
                    'data': get_data(house, "December", clicked)
                }
            ]
        }
    }
    return JsonResponse(chart, safe=False)

# check if user belongs to a house
def checkHouse(request):
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    if use.profile.house is None:
        return True
    return False

# displays all the members in the house
@login_required
def house(request):
    if checkHouse(request):
        return redirect('house_error')
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    house = getHouse(request)
    return render(request, 'ChurroApp/house.html', {'Profiles': profiles, 'house': house})

@login_required
def house_error(request):
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    return render(request, 'ChurroApp/houseerror.html', {'name': use})

# unique string that allows a user to join a house
def generateHouseCode():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    set = Profile.objects.filter(house=code)
    while( len(set) > 0):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        set = Profile.objects.filter(house=code)
    return code

# creating a new house, generates a new code, user can choose the name of their
# house, and saves the current user to that house
@login_required
def house_new(request):
    if request.method == "POST":
        form = HouseForm(request.POST)
        if(form.is_valid()):
            house = House()
            code = generateHouseCode()
            house.name = form.cleaned_data['house_name']
            house.code = code
            house.joined = True;
            house.save()
            current_user = request.user
            use = User.objects.get(pk = current_user.id)
            use.profile.house = code
            use.save()
            return redirect('house')
    else:
        form = HouseForm()

    return render(request, 'ChurroApp/house_edit.html',{'form': form})

# asks a user to input a join code, if it exists adds and saves them
# to that house, if successful redirects them to the house page
@login_required
def house_join(request):
    if request.method == "POST":
        form = HouseJoinForm(request.POST)
        if(form.is_valid()):
            current_user = request.user
            use = User.objects.get(pk = current_user.id)
            house = House.objects.filter(code = form.cleaned_data['house_code'])
            if(len(house) < 1):
                return redirect('house_join')
            houseObject = house[0]
            if houseObject.joined == False:
                return redirect('house_join')
            use.profile.house = form.cleaned_data['house_code']
            use.save()
            return redirect('house')
    else:
        form = HouseJoinForm()
    return render(request, 'ChurroApp/house_join.html', {'form': form})

# if the user clicks the button on the house page, toggles whether someone
# is able to joing the house or not
@login_required
def toggle_joinable(request):
    if checkHouse(request):
        return redirect('house_error')
    house = getHouse(request)
    if house.joined == True:
        house.joined = False
    else:
        house.joined = True
    house.save()
    return redirect('house')

# finds the house associated with the current user
def getHouse(request):
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    return get_object_or_404(House, code = use.profile.house)

@login_required
def delete_member(request, pk):
    if checkHouse(request):
        return redirect('house_error')
    member = get_object_or_404(Profile,pk=pk)
    house = getHouse(request)
    if member.house != house.code:
        return redirect('dashboard')
    member.house = None;
    member.save();
    return redirect('house')

# filters the bills into three categories: overdue, due, and paid. Then renders to the HTML where
# it displays these categories into different tables
@login_required
def bills(request):
    if checkHouse(request):
        return redirect('house_error')
    house = getHouse(request)
    due_bills = Bill.objects.filter(house_id = house, status=False, due_date__gte = datetime.date.today()).order_by('due_date')
    paid_bills = Bill.objects.filter(house_id = house, status=True, due_date__gte = datetime.date.today()+timedelta(days=-2*30)).order_by('-due_date')
    overdue_bills = Bill.objects.filter(house_id = house, status=False, due_date__lt = datetime.date.today()).order_by('due_date')
    return render(request, 'ChurroApp/bills.html', {'due_bills': due_bills, 'paid_bills': paid_bills, 'overdue_bills': overdue_bills})

# changes status of bills if user clicks paid tick button, depending on frequency of bill,
# creates new bill for the next date
@login_required
def bill_complete(request,pk):
    if checkHouse(request):
        return redirect('house_error')

    old_bill = get_object_or_404(Bill, pk=pk)
    house = getHouse(request)
    if old_bill.house_id != house:
        return redirect('dashboard')

    if old_bill.status == 0:
        old_bill.status = True;
        old_bill.save()

        if old_bill.frequency == 'ONCEOFF':
            #dont create a new bill!
            return redirect('bills')

        else:
            #create a new bill rotating to the next user in case this is a recurring bill
            bill = Bill()
            bill.house_id = old_bill.house_id
            bill.name = old_bill.name
            bill.frequency = old_bill.frequency
            bill.total_amount = old_bill.total_amount
            bill.bill_split = old_bill.bill_split

            #jump forward the specified time frame
            # couldnt get it working in a seperate function
            # only works in reference to days and weeks not months/years
            # but this is usually how chores work anyway so idk
            if old_bill.frequency == 'DAILY':
                bill.due_date = old_bill.due_date + datetime.timedelta(days = 1)
            elif old_bill.frequency == 'WEEKLY':
                bill.due_date = old_bill.due_date + datetime.timedelta(days = 7)
            elif old_bill.frequency == 'FORTNIGHTLY':
                bill.due_date = old_bill.due_date + datetime.timedelta(weeks = 2)
            elif old_bill.frequency == 'MONTHLY':
                bill.due_date = old_bill.due_date + datetime.timedelta(weeks = 4)
            elif old_bill.frequency == 'QUARTERLY':
                bill.due_date = old_bill.due_date + datetime.timedelta(weeks = 12)
            elif old_bill.frequency == 'YEARLY':
                bill.due_date = old_bill.due_date + datetime.timedelta(days = 365)
            else:
                bill.due_date = old_bill.due_date + datetime.timedelta(weeks = 4)


            bill.save()
    return redirect('bills')


@login_required
def bill_delete(request,pk):
    if checkHouse(request):
        return redirect('house_error')
    bill = get_object_or_404(Bill, pk=pk)
    house = getHouse(request)
    if bill.house_id != house:
        return redirect('dashboard')
    bill.delete()
    return redirect('bills')


# saves the details of whatever field the user changes if it is valid
@login_required
def bill_edit(request,pk):
    if checkHouse(request):
        return redirect('house_error')
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    house = getHouse(request)
    bill = get_object_or_404(Bill,pk=pk)
    if(house == bill.house_id):
        if request.method == "POST":
            form = BillForm(request.POST)
            if form.is_valid():
                bill.name = form.cleaned_data['bill_name']
                bill.frequency = form.cleaned_data['bill_frequency']
                bill.due_date =  form.cleaned_data['bill_date']
                bill.total_amount =  form.cleaned_data['bill_amount']
                bill.bill_split = (bill.total_amount/len(profiles))
                bill.status =  form.cleaned_data['bill_status']

                bill.save()
                return redirect('bills')
        else:
            form = BillForm(initial={'bill_name': bill.name,'bill_date':bill.due_date,'bill_frequency': bill.frequency,'bill_amount': bill.total_amount,'bill_status': bill.status})
    else:
        return redirect('house')

    return render(request, 'ChurroApp/bill_edit.html', {'form': form})

# if the user belongs to a house, they can create a new bill, and it is saved if the inputs entered is valid
@login_required
def bill_new(request):
    if checkHouse(request):
        return redirect('house_error')
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    if request.method == "POST":
        form = BillForm(request.POST)
        if(form.is_valid()):
            bill = Bill()
            bill.house_id = getHouse(request)
            bill.name = form.cleaned_data['bill_name']
            bill.due_date = form.cleaned_data['bill_date']
            bill.frequency = form.cleaned_data['bill_frequency']
            bill.total_amount = form.cleaned_data['bill_amount']
            bill.bill_split = (bill.total_amount/len(profiles))
            bill.status = form.cleaned_data['bill_status']
            bill.save()
            return redirect('bills')
    else:
        form = BillForm()
    return render(request,'ChurroApp/bill_edit.html',{'form': form})


# gets all the chores for the house of the current user
@login_required
def chores(request):
    if checkHouse(request):
        return redirect('house_error')
    house = getHouse(request)
    chores = Chore.objects.filter(house_id = house, status=False).order_by('date')
    completed_chores = Chore.objects.filter(house_id = house, status=True, date__gte = datetime.date.today()+timedelta(days=-30)).order_by('-date')
    return render(request, 'ChurroApp/chores.html', {'chores': chores, 'completed_chores':completed_chores})

# changes status of chore if user clicks Done tick button, depending on frequency of chore,
# creates new chore for the next rotation and assigns a new house member
@login_required
def chore_complete(request,pk):
    if checkHouse(request):
        return redirect('house_error')
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    house = getHouse(request)
    old_chore = get_object_or_404(Chore, pk=pk)
    if old_chore.house_id != house:
        return redirect('dashboard')

    if old_chore.status == 0:
        old_chore.status = True;
        old_chore.save()

        if old_chore.frequency == 'ONCEOFF':
            #dont create a new chore!
            return redirect('chores')

        else:
            #create a new chore rotating to the next user in case this is a recurring chore_edit
            chore = Chore()
            chore.house_id = old_chore.house_id
            chore.name = old_chore.name

            chore.frequency = old_chore.frequency
            #jump forward the specified time frame
            # couldnt get it working in a seperate function
            # only works in reference to days and weeks not months/years
            # but this is usually how chores work anyway so idk
            if old_chore.frequency == 'DAILY':
                chore.date = old_chore.date + datetime.timedelta(days = 1)
            elif old_chore.frequency == 'WEEKLY':
                chore.date = old_chore.date + datetime.timedelta(days = 7)
            elif old_chore.frequency == 'FORTNIGHTLY':
                chore.date = old_chore.date + datetime.timedelta(weeks = 2)
            elif old_chore.frequency == 'MONTHLY':
                chore.date = old_chore.date + datetime.timedelta(weeks = 4)
            elif old_chore.frequency == 'QUARTERLY':
                chore.date = old_chore.date + datetime.timedelta(weeks = 12)
            elif old_chore.frequency == 'YEARLY':
                chore.date = old_chore.date + datetime.timedelta(days = 365)
            else:
                chore.date = old_chore.date + datetime.timedelta(weeks = 4)


            if old_chore.user_id == profiles[(len(profiles))-1].user:
                chore.user_id = profiles[0].user
            else:
                for i in range(len(profiles)-1):
                    if  old_chore.user_id == profiles[i].user:
                        chore.user_id = profiles[i+1].user
                        break

            chore.save()
            return redirect('chores')

    else:

        return redirect('chores')

@login_required
def chore_delete(request,pk):
    if checkHouse(request):
        return redirect('house_error')
    chore = get_object_or_404(Chore, pk=pk)
    house = getHouse(request)
    if chore.house_id != house:
        return redirect('dashboard')

    chore.delete()
    return redirect('chores')

# saves input data from user when they want to change a field, if it's valid
@login_required
def chore_edit(request,pk):
    house = getHouse(request)
    chore = get_object_or_404(Chore,pk=pk)
    if(house == chore.house_id):
        if checkHouse(request):
            return redirect('house_error')
        chore = get_object_or_404(Chore,pk=pk)
        if request.method == "POST":
            form = ChoreForm(request.POST)
            if form.is_valid():
                chore.name = form.cleaned_data['chore_name']
                chore.date = form.cleaned_data['chore_date']
                chore.status = form.cleaned_data['chore_status']
                chore.frequency = form.cleaned_data['chore_frequency']
                chore.save()
                return redirect('chores')
        else:
            form = ChoreForm(initial={'chore_name': chore.name, 'chore_date': chore.date, 'chore_frequency': chore.frequency, 'chore_status': chore.status})

        return render(request, 'ChurroApp/chore_edit.html', {'form': form})
    else:
        return redirect('house')

# if a user belongs to a house, user can create a new chore and the form is saved
# if the inputs are valid
@login_required
def chore_new(request):
    if checkHouse(request):
        return redirect('house_error')
    #User objects
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    house = getHouse(request)

    if request.method == "POST":
        form = ChoreForm(request.POST)
        if(form.is_valid()):
            #generate random number in the pool of house users to start the chore_edit
            random_number = (randint(0, len(profiles)-1))
            chore = Chore()
            chore.house_id = getHouse(request)
            chore.name = form.cleaned_data['chore_name']
            #assign a random memeber to the chore
            try:
                chore.user_id = profiles[random_number].user
            except:
                chore.user_id = random_number

            chore.date = form.cleaned_data['chore_date']
            chore.status = form.cleaned_data['chore_status']
            chore.frequency = form.cleaned_data['chore_frequency']

            # set the published date to todays date
            now = datetime.datetime.now()
            chore.published_date = now
            chore.save()
            return redirect('chores')
    else:
        form = ChoreForm()

    return render(request,'ChurroApp/chore_edit.html',{'form': form})

# if a user belongs to a house, gets all the items for their house
@login_required
def items(request):
    if checkHouse(request):
        return redirect('house_error')
    house = getHouse(request)
    items = Shared_Item.objects.filter(house_id=house).order_by('last_restock')
    return render(request, 'ChurroApp/items.html', {'items':items})

# if user clicks the restocked button, changes the status of the
# item to high and the date they bought it, and assigns a new user to buy the item next time
@login_required
def item_complete(request,pk):
    if checkHouse(request):
        return redirect('house_error')
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    house = getHouse(request)
    done_item = get_object_or_404(Shared_Item,pk=pk)

    if done_item.house_id != house:
        return redirect('dashboard')

    if done_item.done == 0:
        done_item.done = True;
        done_item.save()

        item = Shared_Item()
        item.house_id = done_item.house_id
        item.name = done_item.name
        item.status = "High"
        if done_item.user_id == profiles[(len(profiles))-1].user:
            item.user_id = profiles[0].user
        else:
            for i in range(len(profiles)-1):
                if done_item.user_id == profiles[i].user:
                    item.user_id = profiles[i+1].user
                    break
        item.last_restock = datetime.date.today()
        item.save()
        done_item.delete()
    return redirect('items')

@login_required
def item_delete(request,pk):
    if checkHouse(request):
        return redirect('house_error')
    item = get_object_or_404(Shared_Item,pk=pk)
    house = getHouse(request)
    if item.house_id != house:
        return redirect('dashboard')
    item.delete()
    return redirect('items')

# saves the changes the user made to the chore if the inputs
# are valid
@login_required
def item_edit(request,pk):
    if checkHouse(request):
        return redirect('house_error')
    item = get_object_or_404(Shared_Item,pk=pk)
    house = getHouse(request)
    if(house == item.house_id):
        if request.method =="POST":
            form = ItemForm(request.POST)
            if form.is_valid():
                item.house_id = getHouse(request)
                item.name = form.cleaned_data['item_name']
                item.status = form.cleaned_data['item_status']
                item.last_restock = form.cleaned_data['item_LastRestock']
                item.save()
                return redirect('items')
        else:
            form = ItemForm(initial = {'item_name':item.name,'item_status':item.status,'item_LastRestock':item.last_restock})
        return render(request, 'ChurroApp/item_edit.html',{'form':form})
    else:
        return redirect('house')

# if a user belongs to a house, lets them create a new item. Assigns the person to
# buy the item, randomly
@login_required
def item_new(request):
    if checkHouse(request):
        return redirect('house_error')
    current_user = request.user
    use = User.objects.get(pk=current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    house = getHouse(request)

    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            random_number = (randint(0, len(profiles)-1))
            item = Shared_Item()
            item.house_id = getHouse(request)
            item.name = form.cleaned_data['item_name']
            item.status = form.cleaned_data['item_status']
            try:
                item.user_id = profiles[random_number].user
            except:
                item.user_id = random_number
            item.last_restock = form.cleaned_data['item_LastRestock']
            item.save()
            return redirect('items')
    else:
        form = ItemForm()
    return render(request,'ChurroApp/item_edit.html',{'form':form})

# if the user belongs to a house, display all reminders
@login_required
def reminders(request):
    if checkHouse(request):
        return redirect('house_error')
    house = getHouse(request)
    reminders = Reminder.objects.filter(house_id=house)
    return render(request, 'ChurroApp/dashboard.html', {'reminders':reminders})

# saves changes user made to the reminder form, if the input is valid
@login_required
def reminder_edit(request,pk):
    if checkHouse(request):
        return redirect('house_error')
    current_user = request.user
    use = User.objects.get(pk = current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    reminder = get_object_or_404(Reminder,pk=pk)
    house = getHouse(request)
    if(reminder.house_id == house):
        if request.method =="POST":
            form = ReminderForm(request.POST)
            if form.is_valid():
                reminder.house_id = getHouse(request)
                reminder.name = form.cleaned_data['reminder_name']
                reminder.time = form.cleaned_data['reminder_time']
                reminder.date = form.cleaned_data['reminder_date']
                reminder.save()
                return redirect('dashboard')
        else:
            form = ReminderForm(initial = {'reminder_name':reminder.name,'reminder_time':reminder.time,'reminder_date':reminder.date})
        return render(request, 'ChurroApp/reminder_edit.html',{'form':form})
    else:
        return redirect('house')

# if the reminder belongs to a house, lets them create a new reminder for a specific
# time and date
@login_required
def reminder_new(request):
    if checkHouse(request):
        return redirect('house_error')
    current_user = request.user
    use = User.objects.get(pk=current_user.id)
    profiles = Profile.objects.filter(house=use.profile.house)
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = Reminder()
            reminder.house_id = getHouse(request)
            reminder.name = form.cleaned_data['reminder_name']
            reminder.time = form.cleaned_data['reminder_time']
            reminder.date = form.cleaned_data['reminder_date']
            reminder.save()
            return redirect('dashboard')
    else:
        form = ReminderForm()
    return render(request,'ChurroApp/reminder_edit.html',{'form':form})

@login_required
def reminder_delete(request,pk):
    #checking if user is a part of house
    if checkHouse(request):
        return redirect('house_error')
    reminder = get_object_or_404(Reminder, pk=pk)
    house = getHouse(request)
    if reminder.house_id != house:
        return redirect('dashboard')
    reminder.delete()
    return redirect('dashboard')

#api
FullHouse = namedtuple('FullHouse', ('house', 'users', 'chores', 'bills', 'items', 'reminders'))

def getFullHouse(request):
    houseID = getHouse(request)
    choreList = Chore.objects.filter(house_id = houseID)
    billList = Bill.objects.filter(house_id = houseID)
    itemList = Shared_Item.objects.filter(house_id = houseID)
    reminderList = Reminder.objects.filter(house_id = houseID)
    userIDs = Profile.objects.filter(house = houseID.code).values_list('user', flat = True)
    userList = User.objects.filter(pk__in = userIDs)
    fullHouse = FullHouse(house = houseID, chores = choreList, bills = billList, items = itemList, reminders = reminderList, users = userList)
    return fullHouse



@login_required
@csrf_exempt
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def api_house(request):
    if checkHouse(request):
        return Response("You need to be in a house to retrieve data")
    print('method activated')
    if request.method == 'GET':
        print('Get method for house called')
        houseID = getHouse(request)
        choreList = Chore.objects.filter(house_id = houseID)
        billList = Bill.objects.filter(house_id = houseID)
        itemList = Shared_Item.objects.filter(house_id = houseID)
        reminderList = Reminder.objects.filter(house_id = houseID)
        userIDs = Profile.objects.filter(house = houseID.code).values_list('user', flat = True)
        userList = User.objects.filter(pk__in = userIDs)
        fullHouse = FullHouse(house = houseID, chores = choreList, bills = billList, items = itemList, reminders = reminderList, users = userList)

        serializer = FullHouseSerializer(fullHouse)

        return Response(serializer.data)

    elif request.method == 'POST':
        print('Post method for house called')
        serializer = ChoreSerializer(data = request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        house = getHouse(request)
        house.delete()
        current_user = request.user
        use = User.objects.get(pk = current_user.id)
        use.profile.house = None
        use.save()
        return Response("House has been deleted")
    else:
        print("no work")
