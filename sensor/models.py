from django.db import models

class PowerUsageLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    watt = models.FloatField()  # 실시간 전력(W)
    energy_kwh = models.FloatField()  # 누적 사용 전력(kWh)
    is_power_on = models.BooleanField(default=False)  # 에어컨 전원 상태

    def __str__(self):
        return f"{self.timestamp} - {self.watt}W / {self.energy_kwh}kWh / {'ON' if self.is_power_on else 'OFF'}"

class AirconLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField()
    humidity = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - 온도: {self.temperature}°C, 습도: {self.humidity}%"