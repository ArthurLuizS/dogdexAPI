
from django.contrib import admin

# Register your models here.
from .models import Dog, Owner, Health, ServiceRecord, ServiceType, Stay

admin.site.register(Dog)
admin.site.register(Owner)
admin.site.register(Health)
admin.site.register(ServiceType)
admin.site.register(Stay)
admin.site.register(ServiceRecord)