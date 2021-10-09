from django.contrib import admin
from user.models import User, Address, AddressManager
# Register your models here.

admin.site.register(User)
admin.site.register(Address)
