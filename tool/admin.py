from django.contrib import admin
from .models import Item, ExchangeRequest, UserProfile, Category, GroupChat

admin.site.register(Item)
admin.site.register(ExchangeRequest)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(GroupChat)