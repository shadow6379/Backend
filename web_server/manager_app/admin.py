from django.contrib import admin
from manager_app import models

# Register your models here.


class ManagerInfoAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'email', 'gender', 'phone', 'other')


admin.site.register(models.ManagerInfo, ManagerInfoAdmin)
