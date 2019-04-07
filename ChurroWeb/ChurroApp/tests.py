from django.test import TestCase, Client
from .models import Chore, House, Bill, Shared_Item, Profile,Reminder
import datetime

#If you are lost see the documentation https://docs.djangoproject.com/en/1.8/topics/testing/overview/

def createUser(c):
    response = c.post('/ChurroApp/signup/', {'username' : 'TestUser', 'first_name' : 'Test', 'last_name' : 'User', 'email' : 'test@email.com', 'password1' : 'aStrongPassword', 'password2' : 'aStrongPassword'})

def createHouse(c):
    response = c.post('/ChurroApp/house/new/', {'house_name': 'Dev House'}, follow = True)

class TestCases(TestCase):

######################################Security##################################

#-----------------Shaidee-------------#

#CSRF

#SQLi

#XSS

################################################################################
# Creation of User

    def testSignUp(self):

        # The object that will 'act' as a web browser to make requests
        c = Client()

        # Verifies there are currently no profiles
        self.assertEqual(len(Profile.objects.all()), 0)

        # Makes a post request to the sign up page with the information for the form
        # Signup also conviniently logs us in
        #response = c.post('/ChurroApp/signup/', {'username' : 'ye', 'first_name' : 'ya', 'last_name' : 'boi', 'email' : 'boi@email.com', 'password1' : 'tabishugly', 'password2' : 'tabishugly'})
        createUser(c)

        # Verifys that the number of profiles has increased by 1
        self.assertEqual(len(Profile.objects.all()), 1)

# Log in
    def testLogIn(self):
        # Creates/signs up a user and automatically logs them in
        c = Client()
        createUser(c)

        # log them out to test log in
        c.logout()

        # log user in
        response = c.post('/ChurroApp/login/', {'username': 'TestUser', 'password': 'aStrongPassword'}, follow=True)

        # if the log in was successful, it would redirect (FOUND 302) to the dashboard,
        # which would show a house error because a user doesn't belong to a house yet
        self.assertEqual(str(response.redirect_chain), "[('/ChurroApp/dashboard/', 302), ('/ChurroApp/house/houseerror/', 302)]")


# Edit email
    def testEditEmail(self):
        # Create a user
        c = Client()
        createUser(c)

        # verify the original email saved is the one we entered
        user = Profile.objects.get(pk=1).user
        self.assertEqual(user.email, 'test@email.com')

        # attempt to edit email
        response = c.post('/ChurroApp/account/edit', {'email' : 'test_edit@email.com', 'first_name' : 'Test', 'last_name' : 'User', 'password1' : 'aStrongPassword', 'password2' : 'aStrongPassword'}, follow = True)

        # verify that the save has worked and the email has been updated
        user = Profile.objects.get(pk=1).user
        self.assertEqual(user.email, 'test_edit@email.com')

# Edit first_name
    def testEditFirstName(self):
        # Create a user
        c = Client()
        createUser(c)

        # verify the original first name saved is the one we entered
        user = Profile.objects.get(pk=1).user
        self.assertEqual(user.first_name, 'Test')

        # attempt to edit first name
        response = c.post('/ChurroApp/account/edit', {'email' : 'test@email.com', 'first_name' : 'John', 'last_name' : 'User', 'password1' : 'aStrongPassword', 'password2' : 'aStrongPassword'}, follow = True)

        # verify that the save has worked and the first name has been updated
        user = Profile.objects.get(pk=1).user
        self.assertEqual(user.first_name, 'John')


# Edit last_name
    def testEditLastName(self):
        # Create a user
        c = Client()
        createUser(c)

        # verify the original last name saved is the one we entered
        user = Profile.objects.get(pk=1).user
        self.assertEqual(user.last_name, 'User')

        # attempt to edit last name
        response = c.post('/ChurroApp/account/edit', {'email' : 'test@email.com', 'first_name' : 'Test', 'last_name' : 'Smith', 'password1' : 'aStrongPassword', 'password2' : 'aStrongPassword'}, follow = True)

        # verify that the save has worked and the last name has been updated
        user = Profile.objects.get(pk=1).user
        self.assertEqual(user.last_name, 'Smith')

#-----------------Paul-------------#

# Creation of House

    def testCreateHouse(self):

        # Verifies there are currently no houses
        self.assertEqual(len(House.objects.all()), 0)

        # The object that will 'act' as a web browser to make requests
        c = Client()

        # Makes a post request to the sign up page with the information for the form
        # Signup also conviniently logs us in
        createUser(c)

        # Makes a post request to the new house page with the information for the form
        createHouse(c)

        # Verifys that the number of houses has increased by 1
        self.assertEqual(len(House.objects.all()), 1)

        # Verifies that the name of the added house is the name we entered into the form
        self.assertEqual('Dev House', House.objects.get(pk = 1).name)

        # Verifies that the profile which created the house is linked to the new hosue
        self.assertEqual(Profile.objects.get(pk = 1).house, House.objects.get(pk = 1).code)


# Creation of Chore

    def testCreateChore(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'DAILY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('DAILY', chore.frequency)
        self.assertEqual(False, chore.status)


# Creation of Bill

    def testCreateBill(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'DAILY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('DAILY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

# Creation of Item

    def testCreateItem(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no items in the house and in the entire site
        self.assertEqual(len(Shared_Item.objects.all()), 0)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a item
        response = c.post('/ChurroApp/items/new/', {'item_name' : 'Toilet Paper','item_LastRestock' : '2018-10-03','item_status' : "Low"}, follow = True)

        # Verify the new item was created and that it is linked to the house
        self.assertEqual(len(Shared_Item.objects.all()), 1)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 1)

        # Verify the item's attributes are the ones we entered
        item = Shared_Item.objects.get(pk = 1)
        self.assertEqual('Toilet Paper', item.name)
        self.assertEqual('2018-10-03', str(item.last_restock))
        self.assertEqual('Low', item.status)
        self.assertEqual(False, item.done)

# Creation of Reminder

    def testCreateReminder(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no reminders in the house and in the entire site
        self.assertEqual(len(Reminder.objects.all()), 0)
        self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a reminders
        response = c.post('/ChurroApp/reminder/new/', {'reminder_name' : 'Inspection','reminder_date' : '2018-10-03','reminder_time' : "00:00:00"}, follow = True)

        # Verify the new reminder was created and that it is linked to the house
        self.assertEqual(len(Reminder.objects.all()), 1)
        self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 1)

        # Verify the reminder's attributes are the ones we entered
        reminder = Reminder.objects.get(pk = 1)
        self.assertEqual('Inspection', reminder.name)
        self.assertEqual('2018-10-03', str(reminder.date))
        self.assertEqual('00:00:00', str(reminder.time))

# Toggle house joinable

    def testToggleHouseJoinable(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify the house is joinable
        house = House.objects.get(pk = 1)
        self.assertEqual(True, house.joined)

        # Send the request which toggles it to False
        response = c.get('/ChurroApp/house/toggle_joinable', follow = True)

        # Verify the value is now False
        house = House.objects.get(pk = 1)
        self.assertEqual(False, house.joined)

        # Send another request to toggle it back to True
        response = c.get('/ChurroApp/house/toggle_joinable', follow = True)

        # Verify it is now True
        house = House.objects.get(pk = 1)
        self.assertEqual(True, house.joined)

# Join a created House via join Code

    def testJoinCreatedHouse(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Grab the join code of the house
        houseCode = House.objects.get(pk = 1).code

        # Create a new client
        c = Client()

        # Create another account
        response = c.post('/ChurroApp/signup/', {'username' : 'AnotherTestUser', 'first_name' : 'Test', 'last_name' : 'User', 'email' : 'test@email.com', 'password1' : 'aStrongPassword', 'password2' : 'aStrongPassword'})
        # Join the house from a new account using the house's join code
        response = c.post('/ChurroApp/house/join/', {'house_code' : houseCode})

        # Verify that the new account is in the house
        self.assertEqual(2, len(Profile.objects.all()))
        self.assertEqual(2, len(Profile.objects.filter(house = houseCode)))

# Fail trying to join a house with right code

    def testJoinHouseNotJoinable(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Grab the join code of the house
        houseCode = House.objects.get(pk = 1).code

        # Send the request which toggles it to False
        response = c.get('/ChurroApp/house/toggle_joinable', follow = True)

        # Create a new client
        c = Client()

        # Create another account
        response = c.post('/ChurroApp/signup/', {'username' : 'AnotherTestUser', 'first_name' : 'Test', 'last_name' : 'User', 'email' : 'test@email.com', 'password1' : 'aStrongPassword', 'password2' : 'aStrongPassword'})

        # Join the house from a new account using the house's join code
        response = c.post('/ChurroApp/house/join/', {'house_code' : houseCode})

        # Verify that the new account exists but is not in the house
        self.assertEqual(2, len(Profile.objects.all()))
        self.assertEqual(1, len(Profile.objects.filter(house = houseCode)))

# Fail trying to join a house with wrong code

    def testFailJoiningHouseWithWrongCode(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Grab the join code of the house
        houseCode = House.objects.get(pk = 1).code

        # Create a new client
        c = Client()

        # Create another account
        response = c.post('/ChurroApp/signup/', {'username' : 'AnotherTestUser', 'first_name' : 'Test', 'last_name' : 'User', 'email' : 'test@email.com', 'password1' : 'aStrongPassword', 'password2' : 'aStrongPassword'})

        # Join the house from a new account using an invalid join code
        response = c.post('/ChurroApp/house/join/', {'house_code' : ''})

        # Verify that the new account exists but is not in the house
        self.assertEqual(2, len(Profile.objects.all()))
        self.assertEqual(1, len(Profile.objects.filter(house = houseCode)))


################################################################################
#####################Check the values change appropriatly#######################

#-----------------Emma-------------#

# Editing a Chore

    def testEditAChore(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        #create a chore and test its been created correctly
        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'DAILY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('DAILY', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to edit the chore
        response = c.post('/ChurroApp/chores/1/edit/',{'chore_name' : 'Edited','chore_date' : '2018-10-02','chore_frequency' : 'WEEKLY','chore_status' : True}, follow = True)

        #Verify the changes occured
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Edited', chore.name)
        self.assertEqual('2018-10-02', str(chore.date))
        self.assertEqual('WEEKLY', chore.frequency)
        self.assertEqual(True, chore.status)


    # Editing a Bill
    def testEditABill(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'DAILY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('DAILY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #Attempt to edit the bill
        response = c.post('/ChurroApp/bills/1/edit/', {'bill_name' : 'NewBill','bill_date' : '2017-09-04','bill_frequency' : 'MONTHLY','bill_amount' : '2.25', 'bill_status' : False}, follow = True)

        #Check the new values have been saved
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('NewBill', bill.name)
        self.assertEqual('2017-09-04', str(bill.due_date))
        self.assertEqual('MONTHLY', bill.frequency)
        self.assertEqual('2.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)


    # Editing a Reminder
    def testEditAReminder(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no reminders in the house and in the entire site
        self.assertEqual(len(Reminder.objects.all()), 0)
        self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a reminders
        response = c.post('/ChurroApp/reminder/new/', {'reminder_name' : 'Inspection','reminder_date' : '2018-10-03','reminder_time' : "00:00:00"}, follow = True)

        # Verify the new reminder was created and that it is linked to the house
        self.assertEqual(len(Reminder.objects.all()), 1)
        self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 1)

        # Verify the reminder's attributes are the ones we entered
        reminder = Reminder.objects.get(pk = 1)
        self.assertEqual('Inspection', reminder.name)
        self.assertEqual('2018-10-03', str(reminder.date))
        self.assertEqual('00:00:00', str(reminder.time))

        # Edit the Reminder
        response = c.post('/ChurroApp/reminder/1/edit/', {'reminder_name' : 'Fire alarm Check','reminder_date' : '2019-04-12','reminder_time' : "12:34:00"}, follow = True)

        # Check the values were changed
        reminder = Reminder.objects.get(pk = 1)
        self.assertEqual('Fire alarm Check', reminder.name)
        self.assertEqual('2019-04-12', str(reminder.date))
        self.assertEqual('12:34:00', str(reminder.time))


    # Editing an Item
    def testEditAnItem(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no items in the house and in the entire site
        self.assertEqual(len(Shared_Item.objects.all()), 0)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a item
        response = c.post('/ChurroApp/items/new/', {'item_name' : 'Toilet Paper','item_LastRestock' : '2018-10-03','item_status' : "Low"}, follow = True)

        # Verify the new item was created and that it is linked to the house
        self.assertEqual(len(Shared_Item.objects.all()), 1)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 1)

        # Verify the item's attributes are the ones we entered
        item = Shared_Item.objects.get(pk = 1)
        self.assertEqual('Toilet Paper', item.name)
        self.assertEqual('2018-10-03', str(item.last_restock))
        self.assertEqual('Low', item.status)
        self.assertEqual(False, item.done)

        # Attempt to edit the item
        response = c.post('/ChurroApp/items/1/edit/', {'item_name' : 'Dishwashing','item_LastRestock' : '2010-11-07','item_status' : "Empty"}, follow = True)

        # Verify the item was updated
        item = Shared_Item.objects.get(pk = 1)
        self.assertEqual('Dishwashing', item.name)
        self.assertEqual('2010-11-07', str(item.last_restock))
        self.assertEqual('Empty', item.status)
        self.assertEqual(False, item.done)


################################################################################
#####Must check the rotation, status and creation of a new chore/bill/item#####


#-----------------Pearl-------------#
# Make sure you check on completion that it that it creates a new chore and rotates whos assigned and the due date.
# Check the old chore is changed to a completed status

# Completing a Chore (should create a new one dependent on the frequency)

    #ONCEOFF
    def testCompleteOnceOffChore(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        #create a chore and test its been created correctly
        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'ONCEOFF','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('ONCEOFF', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to mark chore Complete
        response = c.post('/ChurroApp/choreComplete/1/')

        #check that a new chore is not created
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        #check if fields for old chore are updated
        chore1 = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore1.name)
        self.assertEqual('2018-10-03', str(chore1.date))
        self.assertEqual('ONCEOFF', chore1.frequency)
        self.assertEqual(True, chore1.status)


    #DAILY
    def testCompleteDailyChore(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        #create a chore and test its been created correctly
        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'DAILY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('DAILY', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to mark chore Complete
        response = c.post('/ChurroApp/choreComplete/1/')

        #check if new chore is created
        self.assertEqual(len(Chore.objects.all()), 2)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 2)

        #check if fields for old chore are updated
        chore1 = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore1.name)
        self.assertEqual('2018-10-03', str(chore1.date))
        self.assertEqual('DAILY', chore1.frequency)
        self.assertEqual(True, chore1.status)

        #check fields for new chore
        chore2 = Chore.objects.get(pk = 2)
        self.assertEqual('Clean', chore2.name)
        self.assertEqual('2018-10-04', str(chore2.date))
        self.assertEqual('DAILY', chore2.frequency)
        self.assertEqual(False, chore2.status)

    #WEEKLY
    def testCompleteWeeklyChore(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        #create a chore and test its been created correctly
        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'WEEKLY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('WEEKLY', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to mark chore Complete
        response = c.post('/ChurroApp/choreComplete/1/')

        #check if new chore is created
        self.assertEqual(len(Chore.objects.all()), 2)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 2)

        #check if fields for old chore are updated
        chore1 = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore1.name)
        self.assertEqual('2018-10-03', str(chore1.date))
        self.assertEqual('WEEKLY', chore1.frequency)
        self.assertEqual(True, chore1.status)

        #check fields for new chore
        chore2 = Chore.objects.get(pk = 2)
        self.assertEqual('Clean', chore2.name)
        self.assertEqual('2018-10-10', str(chore2.date))
        self.assertEqual('WEEKLY', chore2.frequency)
        self.assertEqual(False, chore2.status)

    #FORTNIGHTLY
    def testCompleteFortnightlyChore(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        #create a chore and test its been created correctly
        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'FORTNIGHTLY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('FORTNIGHTLY', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to mark chore Complete
        response = c.post('/ChurroApp/choreComplete/1/')

        #check if new chore is created
        self.assertEqual(len(Chore.objects.all()), 2)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 2)

        #check if fields for old chore are updated
        chore1 = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore1.name)
        self.assertEqual('2018-10-03', str(chore1.date))
        self.assertEqual('FORTNIGHTLY', chore1.frequency)
        self.assertEqual(True, chore1.status)

        #check fields for new chore
        chore2 = Chore.objects.get(pk = 2)
        self.assertEqual('Clean', chore2.name)
        self.assertEqual('2018-10-17', str(chore2.date))
        self.assertEqual('FORTNIGHTLY', chore2.frequency)
        self.assertEqual(False, chore2.status)

    #MONTHLY
    def testCompleteMonthlyChore(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        #create a chore and test its been created correctly
        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'MONTHLY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('MONTHLY', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to mark chore Complete
        response = c.post('/ChurroApp/choreComplete/1/')

        #check if new chore is created
        self.assertEqual(len(Chore.objects.all()), 2)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 2)

        #check if fields for old chore are updated
        chore1 = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore1.name)
        self.assertEqual('2018-10-03', str(chore1.date))
        self.assertEqual('MONTHLY', chore1.frequency)
        self.assertEqual(True, chore1.status)

        #check fields for new chore
        chore2 = Chore.objects.get(pk = 2)
        self.assertEqual('Clean', chore2.name)
        self.assertEqual('2018-10-31', str(chore2.date))
        self.assertEqual('MONTHLY', chore2.frequency)
        self.assertEqual(False, chore2.status)

    #QUARTERLY
    def testCompleteQuarterlyChore(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        #create a chore and test its been created correctly
        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'QUARTERLY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('QUARTERLY', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to mark chore Complete
        response = c.post('/ChurroApp/choreComplete/1/')

        #check if new chore is created
        self.assertEqual(len(Chore.objects.all()), 2)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 2)

        #check if fields for old chore are updated
        chore1 = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore1.name)
        self.assertEqual('2018-10-03', str(chore1.date))
        self.assertEqual('QUARTERLY', chore1.frequency)
        self.assertEqual(True, chore1.status)

        #check fields for new chore
        chore2 = Chore.objects.get(pk = 2)
        self.assertEqual('Clean', chore2.name)
        self.assertEqual('2018-12-26', str(chore2.date))
        self.assertEqual('QUARTERLY', chore2.frequency)
        self.assertEqual(False, chore2.status)

    #YEARLY
    def testCompleteYearlyChore(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        #create a chore and test its been created correctly
        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'YEARLY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('YEARLY', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to mark chore Complete
        response = c.post('/ChurroApp/choreComplete/1/')

        #check if new chore is created
        self.assertEqual(len(Chore.objects.all()), 2)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 2)

        #check if fields for old chore are updated
        chore1 = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore1.name)
        self.assertEqual('2018-10-03', str(chore1.date))
        self.assertEqual('YEARLY', chore1.frequency)
        self.assertEqual(True, chore1.status)

        #check fields for new chore
        chore2 = Chore.objects.get(pk = 2)
        self.assertEqual('Clean', chore2.name)
        self.assertEqual('2019-10-03', str(chore2.date))
        self.assertEqual('YEARLY', chore2.frequency)
        self.assertEqual(False, chore2.status)


# Marking a Bill as paid (should create a new one dependent on the frequency)

    #ONCEOFF
    def testOnceOffBillPaid(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'ONCEOFF','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('ONCEOFF', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #attempt to mark a bill as paid
        response = c.post('/ChurroApp/billComplete/1/')

        #check that new a bill is not created
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        #check if bill updated
        bill1 = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill1.name)
        self.assertEqual('2018-10-03', str(bill1.due_date))
        self.assertEqual('ONCEOFF', bill1.frequency)
        self.assertEqual('25.25', str(bill1.total_amount))
        self.assertEqual(True, bill1.status)


    #DAILY
    def testDailyBillPaid(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'DAILY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('DAILY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #attempt to mark a bill as paid
        response = c.post('/ChurroApp/billComplete/1/')

        #check if new bill created
        self.assertEqual(len(Bill.objects.all()), 2)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 2)

        #check if bill updated
        bill1 = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill1.name)
        self.assertEqual('2018-10-03', str(bill1.due_date))
        self.assertEqual('DAILY', bill1.frequency)
        self.assertEqual('25.25', str(bill1.total_amount))
        self.assertEqual(True, bill1.status)

        #check if bill updated
        bill2 = Bill.objects.get(pk = 2)
        self.assertEqual('Rent', bill2.name)
        self.assertEqual('2018-10-04', str(bill2.due_date))
        self.assertEqual('DAILY', bill2.frequency)
        self.assertEqual('25.25', str(bill2.total_amount))
        self.assertEqual(False, bill2.status)

    #WEEKLY
    def testWeeklyBillPaid(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'WEEKLY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('WEEKLY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #attempt to mark a bill as paid
        response = c.post('/ChurroApp/billComplete/1/')

        #check if new bill created
        self.assertEqual(len(Bill.objects.all()), 2)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 2)

        #check if bill updated
        bill1 = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill1.name)
        self.assertEqual('2018-10-03', str(bill1.due_date))
        self.assertEqual('WEEKLY', bill1.frequency)
        self.assertEqual('25.25', str(bill1.total_amount))
        self.assertEqual(True, bill1.status)

        #check if bill updated
        bill2 = Bill.objects.get(pk = 2)
        self.assertEqual('Rent', bill2.name)
        self.assertEqual('2018-10-10', str(bill2.due_date))
        self.assertEqual('WEEKLY', bill2.frequency)
        self.assertEqual('25.25', str(bill2.total_amount))
        self.assertEqual(False, bill2.status)

    #FORTNIGHTLY
    def testFortnightlyBillPaid(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'FORTNIGHTLY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('FORTNIGHTLY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #attempt to mark a bill as paid
        response = c.post('/ChurroApp/billComplete/1/')

        #check if new bill created
        self.assertEqual(len(Bill.objects.all()), 2)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 2)

        #check if bill updated
        bill1 = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill1.name)
        self.assertEqual('2018-10-03', str(bill1.due_date))
        self.assertEqual('FORTNIGHTLY', bill1.frequency)
        self.assertEqual('25.25', str(bill1.total_amount))
        self.assertEqual(True, bill1.status)

        #check if bill updated
        bill2 = Bill.objects.get(pk = 2)
        self.assertEqual('Rent', bill2.name)
        self.assertEqual('2018-10-17', str(bill2.due_date))
        self.assertEqual('FORTNIGHTLY', bill2.frequency)
        self.assertEqual('25.25', str(bill2.total_amount))
        self.assertEqual(False, bill2.status)

    #MONTHLY
    def testMonthlyBillPaid(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'MONTHLY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('MONTHLY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #attempt to mark a bill as paid
        response = c.post('/ChurroApp/billComplete/1/')

        #check if new bill created
        self.assertEqual(len(Bill.objects.all()), 2)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 2)

        #check if bill updated
        bill1 = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill1.name)
        self.assertEqual('2018-10-03', str(bill1.due_date))
        self.assertEqual('MONTHLY', bill1.frequency)
        self.assertEqual('25.25', str(bill1.total_amount))
        self.assertEqual(True, bill1.status)

        #check if bill updated
        bill2 = Bill.objects.get(pk = 2)
        self.assertEqual('Rent', bill2.name)
        self.assertEqual('2018-10-31', str(bill2.due_date))
        self.assertEqual('MONTHLY', bill2.frequency)
        self.assertEqual('25.25', str(bill2.total_amount))
        self.assertEqual(False, bill2.status)

    #QUARTERLY
    def testQuarterlyBillPaid(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'QUARTERLY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('QUARTERLY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #attempt to mark a bill as paid
        response = c.post('/ChurroApp/billComplete/1/')

        #check if new bill created
        self.assertEqual(len(Bill.objects.all()), 2)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 2)

        #check if bill updated
        bill1 = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill1.name)
        self.assertEqual('2018-10-03', str(bill1.due_date))
        self.assertEqual('QUARTERLY', bill1.frequency)
        self.assertEqual('25.25', str(bill1.total_amount))
        self.assertEqual(True, bill1.status)

        #check if bill updated
        bill2 = Bill.objects.get(pk = 2)
        self.assertEqual('Rent', bill2.name)
        self.assertEqual('2018-12-26', str(bill2.due_date))
        self.assertEqual('QUARTERLY', bill2.frequency)
        self.assertEqual('25.25', str(bill2.total_amount))
        self.assertEqual(False, bill2.status)

    #YEARLY
    def testYearlyBillPaid(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'YEARLY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('YEARLY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #attempt to mark a bill as paid
        response = c.post('/ChurroApp/billComplete/1/')

        #check if new bill created
        self.assertEqual(len(Bill.objects.all()), 2)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 2)

        #check if bill updated
        bill1 = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill1.name)
        self.assertEqual('2018-10-03', str(bill1.due_date))
        self.assertEqual('YEARLY', bill1.frequency)
        self.assertEqual('25.25', str(bill1.total_amount))
        self.assertEqual(True, bill1.status)

        #check if bill updated
        bill2 = Bill.objects.get(pk = 2)
        self.assertEqual('Rent', bill2.name)
        self.assertEqual('2019-10-03', str(bill2.due_date))
        self.assertEqual('YEARLY', bill2.frequency)
        self.assertEqual('25.25', str(bill2.total_amount))
        self.assertEqual(False, bill2.status)

# Marking an Item as bought
    def testItemRestocked(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no items in the house and in the entire site
        self.assertEqual(len(Shared_Item.objects.all()), 0)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a item
        response = c.post('/ChurroApp/items/new/', {'item_name' : 'Toilet Paper','item_LastRestock' : '2018-10-03','item_status' : "Low"}, follow = True)

        # Verify the new item was created and that it is linked to the house
        self.assertEqual(len(Shared_Item.objects.all()), 1)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 1)

        # Verify the item's attributes are the ones we entered
        item = Shared_Item.objects.get(pk = 1)
        self.assertEqual('Toilet Paper', item.name)
        self.assertEqual('2018-10-03', str(item.last_restock))
        self.assertEqual('Low', item.status)
        self.assertEqual(False, item.done)

        #attempt restocking a low item
        response = c.post('/ChurroApp/items/1/Complete/')

        #making sure a new item was created and previous one was delted
        self.assertEqual(len(Shared_Item.objects.all()), 1)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 1)

        #checking if item was updated
        date = datetime.date.today()
        newitem = Shared_Item.objects.get(pk = 2)
        self.assertEqual('Toilet Paper', newitem.name)
        self.assertEqual(str(date), str(newitem.last_restock))
        self.assertEqual('High', newitem.status)
        self.assertEqual(False, newitem.done)


# Reminder push notification
    def testReminders(self):
        def testDeleteReminder(self):
            # Setup environment for the test
            c = Client()
            createUser(c)
            createHouse(c)

            # Verify there are no reminders in the house and in the entire site
            self.assertEqual(len(Reminder.objects.all()), 0)
            self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 0)

            # Make the Post request to create a reminders
            response = c.post('/ChurroApp/reminder/new/', {'reminder_name' : 'Inspection','reminder_date' : '2018-10-03','reminder_time' : "00:00:00"}, follow = True)

            # Verify the new reminder was created and that it is linked to the house
            self.assertEqual(len(Reminder.objects.all()), 1)
            self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 1)

            # Verify the reminder's attributes are the ones we entered
            reminder = Reminder.objects.get(pk = 1)
            self.assertEqual('Inspection', reminder.name)
            self.assertEqual('2018-10-03', str(reminder.date))
            self.assertEqual('00:00:00', str(reminder.time))

            #reminder Response
            response = c.post('/ChurroApp/reminder/')

            #checking if reminders work
            self.assertEqual(response.status_code,'200')


###############################################################################
##################################Deleting#####################################

# Deleting a Chore
    def testDeleteChore(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore
        response = c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03','chore_frequency' : 'DAILY','chore_status' : False}, follow = True)

        # Verify the new chore was created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 1)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 1)

        # Verify the chore's attributes are the ones we entered
        chore = Chore.objects.get(pk = 1)
        self.assertEqual('Clean', chore.name)
        self.assertEqual('2018-10-03', str(chore.date))
        self.assertEqual('DAILY', chore.frequency)
        self.assertEqual(False, chore.status)

        #attempt to delete a chore
        response = c.post('/ChurroApp/choreDelete/1/')

        #check that there are no chores for house
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

# Deleting a Bill
    def testDeleteBill(self):

        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill
        response = c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent','bill_date' : '2018-10-03','bill_frequency' : 'DAILY','bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Verify the new bill was created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 1)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 1)

        # Verify the bill's attributes are the ones we entered
        bill = Bill.objects.get(pk = 1)
        self.assertEqual('Rent', bill.name)
        self.assertEqual('2018-10-03', str(bill.due_date))
        self.assertEqual('DAILY', bill.frequency)
        self.assertEqual('25.25', str(bill.total_amount))
        self.assertEqual(False, bill.status)

        #attempt to delete a bill
        response = c.post('/ChurroApp/billDelete/1/')

        #check that there are no bill for house
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

# Deleting an Item

    def testDeleteItem(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no items in the house and in the entire site
        self.assertEqual(len(Shared_Item.objects.all()), 0)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a item
        response = c.post('/ChurroApp/items/new/', {'item_name' : 'Toilet Paper','item_LastRestock' : '2018-10-03','item_status' : "Low"}, follow = True)

        # Verify the new item was created and that it is linked to the house
        self.assertEqual(len(Shared_Item.objects.all()), 1)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 1)

        # Verify the item's attributes are the ones we entered
        item = Shared_Item.objects.get(pk = 1)
        self.assertEqual('Toilet Paper', item.name)
        self.assertEqual('2018-10-03', str(item.last_restock))
        self.assertEqual('Low', item.status)
        self.assertEqual(False, item.done)

        #attempt to delete an item
        response = c.post('/ChurroApp/items/1/delete/')

        #check that there are no items for house
        self.assertEqual(len(Shared_Item.objects.all()), 0)
        self.assertEqual(len(Shared_Item.objects.filter(house_id = 1)), 0)

# Deleting a Reminder
    def testDeleteReminder(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no reminders in the house and in the entire site
        self.assertEqual(len(Reminder.objects.all()), 0)
        self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a reminders
        response = c.post('/ChurroApp/reminder/new/', {'reminder_name' : 'Inspection','reminder_date' : '2018-10-03','reminder_time' : "00:00:00"}, follow = True)

        # Verify the new reminder was created and that it is linked to the house
        self.assertEqual(len(Reminder.objects.all()), 1)
        self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 1)

        # Verify the reminder's attributes are the ones we entered
        reminder = Reminder.objects.get(pk = 1)
        self.assertEqual('Inspection', reminder.name)
        self.assertEqual('2018-10-03', str(reminder.date))
        self.assertEqual('00:00:00', str(reminder.time))

        #attempt to delete a reminder
        response = c.post('/ChurroApp/reminderDelete/1/')

        #check that there are no reminders for house
        self.assertEqual(len(Reminder.objects.all()), 0)
        self.assertEqual(len(Reminder.objects.filter(house_id = 1)), 0)

# Remove a house member
    def testRemoveHouseMember(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Grab the join code of the house
        houseCode = House.objects.get(pk = 1).code

        # Create a new client
        c = Client()

        # Create another account
        response = c.post('/ChurroApp/signup/', {'username' : 'AnotherTestUser', 'first_name' : 'Test', 'last_name' : 'User', 'email' : 'test@email.com', 'password1' : 'aStrongPassword', 'password2' : 'aStrongPassword'})
        # Join the house from a new account using the house's join code
        response = c.post('/ChurroApp/house/join/', {'house_code' : houseCode})

        # Verify that the new account is in the house
        self.assertEqual(len(Profile.objects.all()), 2)
        self.assertEqual(len(Profile.objects.filter(house = houseCode)), 2)

        #delete a house member
        response = c.post('/ChurroApp/house/DeleteMember/1')

        #check that there is only 1 member for house and 2 accounts in the database
        self.assertEqual(len(Profile.objects.all()), 2)
        self.assertEqual(len(Profile.objects.filter(house = houseCode)), 1)


# Sign out
    def testSignOut(self):
        # Setup environment for the test which automatically log a user in
        c = Client()
        createUser(c)

        #attempt to Sign Out
        c.logout()

        #check response code
        response = c.get('/ChurroApp/logoutsuccess/')

        #if user was signed out page redirects to landing Page
        self.assertEqual(response.status_code, 200)

###############################################################################
##################################Semantics#####################################
#-----------------Shaidee-------------#

    def testBillsTableGrouping(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no bills in the house and in the entire site
        self.assertEqual(len(Bill.objects.all()), 0)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a bill that is overdue
        c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent', 'bill_date' : '2018-10-03', 'bill_frequency' : 'DAILY', 'bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Make the Post request to create a bill that is upcoming
        c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent', 'bill_date' : '2019-01-01', 'bill_frequency' : 'DAILY', 'bill_amount' : '25.25', 'bill_status' : False}, follow = True)

        # Make the Post request to create a bill that is already paid
        c.post('/ChurroApp/bills/new/', {'bill_name' : 'Rent', 'bill_date' : '2018-10-03', 'bill_frequency' : 'DAILY', 'bill_amount' : '25.25', 'bill_status' : True}, follow = True)

        # Verify the new bills were created and that it is linked to the house
        self.assertEqual(len(Bill.objects.all()), 3)
        self.assertEqual(len(Bill.objects.filter(house_id = 1)), 3)

        # get the bills for this user's house
        bills = Bill.objects.filter(house_id = 1)

        # groups the bills are sorted into for table display on the bills page
        overdue = []
        upcoming = []
        paid = []

        current_date = datetime.date.today()

        for bill in bills:
            if bill.status == False:
                if bill.due_date >= current_date:
                    upcoming.append(bill)
                else:
                    overdue.append(bill)
            else:
                paid.append(bill)

        # verify that the bills were sorted into the correct groups
        self.assertEqual(len(overdue), 1)
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(len(paid), 1)

    def testChoresTableGrouping(self):
        # Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)

        # Verify there are no chores in the house and in the entire site
        self.assertEqual(len(Chore.objects.all()), 0)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 0)

        # Make the Post request to create a chore that has not been completed
        c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean','chore_date' : '2018-10-03', 'chore_frequency' : 'DAILY','chore_status' : False}, follow = True)

        # Make the Post request to create a chore that has been completed
        c.post('/ChurroApp/chores/new/', {'chore_name' : 'Clean', 'chore_date' : '2018-10-03', 'chore_frequency' : 'DAILY','chore_status' : True}, follow = True)

        # Verify the new chores were created and that it is linked to the house
        self.assertEqual(len(Chore.objects.all()), 2)
        self.assertEqual(len(Chore.objects.filter(house_id = 1)), 2)

        # tables the chores are sorted into on the chores page
        completed = []
        uncompleted = []

        # Verify the chore's attributes are the ones we entered
        chores = Chore.objects.filter(house_id = 1)

        for chore in chores:
            if chore.status == False:
                uncompleted.append(chore)
            else:
                completed.append(chore)

        # verify that the chores were sorted into the correct groups
        self.assertEqual(len(completed), 1)
        self.assertEqual(len(uncompleted), 1)
		
	
    def testApi(self):
		
		# Setup environment for the test
        c = Client()
        createUser(c)
        createHouse(c)
		
        response = c.get('/ChurroApp/api/houseList/')
		
        print(response.data)
		
		
		
		
		
		
		
