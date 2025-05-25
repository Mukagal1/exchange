"""
URL configuration for tools project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('main/', views.main_page, name='main_page'),
    path('items/', views.place, name='place'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/<int:item_id>/offer/', views.offer_exchange, name='offer_exchange'),
    path('myitems/', views.my_items, name='myitems'),
    path('items/delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('additem/', views.add_item, name='additem'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('notifications/count/', views.unread_notifications_count, name='unread_notifications_count'),
    path("notifications/accept/<int:request_id>/", views.accept_exchange, name="accept_exchange"),
    path("notifications/reject/<int:request_id>/", views.decline_exchange, name="reject_exchange"),
    path('profile/', views.profile, name='profile'),
    path('profile/update-avatar/', views.update_avatar, name='update_avatar'),
    path('place/', views.place, name='place'),
    path("chats/", views.group_chats, name="group_chats"),
    path("chats/<int:chat_id>/", views.group_chat_detail, name="group_chat_detail"),
    path("chats/<int:chat_id>/join/", views.join_group_chat, name="join_group_chat"),
    path("chats/create/", views.create_group_chat, name="create_group_chat"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
