from django.contrib import admin

# Register your models here.
from .models import Dog, Owner, Health

admin.site.register(Dog)
admin.site.register(Owner)
admin.site.register(Health)