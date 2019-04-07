from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls import url

from . import views

urlpatterns = [
	path(
        'login/',
        auth_views.LoginView.as_view(template_name='ChurroApp/login.html'),
		name='login'
    ),
	path(
        'logout/',
        auth_views.LogoutView.as_view(),
		name='logout'
    ),
	path('', views.landing, name='landing'),

	path('signup/', views.signup, name='signup'),
	path('dashboard/', views.dashboard, name='dashboard'),
	path('house/', views.house, name='house'),
	path('chores', views.chores, name='chores'),
	path('bills/', views.bills, name='bills'),
	path('items/', views.items, name='items'),
	path('logoutsuccess/', views.logoutsuccess, name='logoutsuccess'),
	path('loginfailure/', views.loginfailure, name='loginfailure'),
	path('houseerror/', views.houseerror, name='houseerror'),
	path('account/', views.account, name='account'),
	path('account/edit', views.edit_account, name='edit_account'),


	# Cant have the below path blank since blank is already defined as the landing page

	#paths for Chores
    path('chores/<int:pk>/edit/', views.chore_edit, name='chore_edit'),
    path('chores/new/',views.chore_new, name='chore_new'),
    path('choreComplete/<int:pk>/', views.chore_complete, name="chore_complete"),
    path('choreDelete/<int:pk>/', views.chore_delete, name="chore_delete"),

	#paths for House
    path('house/new/', views.house_new, name='house_new'),
	path('house/join/', views.house_join, name="house_join"),
	path('house/houseerror/', views.house_error, name='house_error'),
	path('house/DeleteMember/<int:pk>', views.delete_member, name='delete_member'),
	path('house/toggle_joinable', views.toggle_joinable, name='toggle_joinable'),

	#paths for Bills
    path('bills/<int:pk>/edit/', views.bill_edit, name='bill_edit'),
    path('bills/new/',views.bill_new, name='bill_new'),
    path('billComplete/<int:pk>/', views.bill_complete, name="bill_complete"),
    path('billDelete/<int:pk>/', views.bill_delete, name="bill_delete"),
	path('bills/data/', views.chart_data, name='chart_data'),

    #paths for Shared Items
    path('items/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('items/new/',views.item_new, name='item_new'),
    path('items/<int:pk>/delete/', views.item_delete, name='item_delete'),
	path('items/<int:pk>/Complete/', views.item_complete, name="item_complete"),

	#paths for Reminders
	path('reminders/', views.reminders, name='reminders'),
	path('reminder/<int:pk>/edit/', views.reminder_edit, name='reminder_edit'),
	path('reminder/new/',views.reminder_new, name='reminder_new'),
	path('reminderDelete/<int:pk>/', views.reminder_delete, name='reminder_delete'),

	path('api/houseList/', views.api_house, name="api_house")

]
