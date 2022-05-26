from django.contrib import admin

from .models import Category, Family, Operation
# Register your models here.

admin.site.register(Category)
admin.site.register(Family)
admin.site.register(Operation)
# admin.site.register(FamilyUsers)

