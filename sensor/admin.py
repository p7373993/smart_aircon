from django.contrib import admin
from .models import AirconUsageLog, PowerUsageLog, AirconLog

class PowerUsageLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'watt', 'energy_kwh', 'is_power_on')

class AirconLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'humidity')

class AirconUsageLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'is_aircon_on')
    list_filter = ('is_aircon_on', 'timestamp')
    ordering = ('-timestamp',)

admin.site.register(PowerUsageLog, PowerUsageLogAdmin)
admin.site.register(AirconLog, AirconLogAdmin)
admin.site.register(AirconUsageLog, AirconUsageLogAdmin)