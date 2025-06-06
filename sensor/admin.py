from django.contrib import admin
from .models import PowerUsageLog, AirconLog

class PowerUsageLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'watt', 'energy_kwh', 'is_power_on')

class AirconLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'humidity')

admin.site.register(PowerUsageLog, PowerUsageLogAdmin)
admin.site.register(AirconLog, AirconLogAdmin)
