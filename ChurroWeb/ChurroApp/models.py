from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Permission, User
from django.db.models.signals import post_save
from django.dispatch import receiver

DAILY = 'DAILY'
WEEKLY = 'WEEKLY'
FORTNIGHTLY = 'FORTNIGHTLY'
MONTHLY = 'MONTHLY'
QUARTERLY = 'QUARTERLY'
YEARLY = 'YEARLY'
ONCEOFF = 'ONCEOFF'
FreqFields = (
    (DAILY, 'Daily'),
    (WEEKLY, 'Weekly'),
    (FORTNIGHTLY, 'Fortnightly'),
	(MONTHLY, 'Monthly'),
	(QUARTERLY, 'Quarterly'),
	(YEARLY, 'Yearly'),
    (ONCEOFF, 'Once Off')
)

Status_Choice = (
    ('Empty','Empty'),
    ('Low','Low'),
    ('High','High'),
)

class House(models.Model):
	name = models.CharField(max_length=20)
	code = models.CharField(max_length=50, null = True, blank=True)
	joined = models.BooleanField(max_length=50, null = True, blank=True)
	def __str__(self):
		return self.name


class Shared_Item(models.Model):
	house_id = models.ForeignKey(
		House,
		on_delete=models.CASCADE)
	user_id = models.ForeignKey(
		User,
		null=True,
		on_delete=models.SET_NULL)
	name = models.CharField(max_length=30)
	status = models.CharField(max_length=1,choices=Status_Choice)
	last_restock = models.DateField()
	#buyer = models.CharField(max_length=30,default=None)
	done = models.BooleanField(default=0)

	def restock(self):
		self.last_restock = timezone.now()
		self.save()

	def __str__(self):
		return self.name

class Chore(models.Model):

	house_id = models.ForeignKey(
		House,
		on_delete=models.CASCADE)
	user_id = models.ForeignKey(
		User,
		null=True,
		on_delete=models.SET_NULL)
	name = models.CharField(max_length=50)
	date = models.DateField()
	#FreqFields = (('Option 1', 'Daily'),('Option 2', 'Weekly'),('Option 3', 'Fortnightly'),('Option 4', 'Monthly'),('Option 5', 'Quarterly'),('Option 6', 'Yearly'))
	frequency = models.CharField(choices = FreqFields,max_length=20, default='Weekly')
	status = models.BooleanField(default=0)
	#published_date = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return self.name

class Reminder(models.Model):
	house_id = models.ForeignKey(
		House,
		on_delete=models.CASCADE)
	name = models.CharField(max_length=40)
	time = models.TimeField()
	date = models.DateField()
	alert = models.DateField(blank=True, null=True)
	frequency = models.CharField(choices = FreqFields,max_length=20)
	status = models.BooleanField(default=0)

	def __str__(self):
		return self.name

class Bill(models.Model):
	house_id = models.ForeignKey(
		House,
		on_delete=models.CASCADE)
	name = models.CharField(max_length=60)
	due_date = models.DateField()
	frequency = models.CharField(max_length=60)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2)
	bill_split = models.DecimalField(max_digits=10, decimal_places=2,default = 0)
	status = models.BooleanField(default=0)

	def __str__(self):
		return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    house = models.CharField(max_length=50, null = True, blank=True)

	#This should probably be defined in a different file for best practice
	# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
