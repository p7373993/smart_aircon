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
    
class AirconUsageLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    is_aircon_on = models.BooleanField(default=False)  # 에어컨 전원 상태
    usage_duration = models.FloatField(default=0.0)    # 사용 시간(분 등, 필요시)

    def __str__(self):
        return f"{self.timestamp} - 에어컨 상태: {'ON' if self.is_aircon_on else 'OFF'}, 사용 시간: {self.usage_duration}분"
    
class UserAirconSettings(models.Model):
    """에어컨 자동 제어 설정"""
    target_temp_max = models.FloatField(default=28.0, help_text="에어컨 켜는 온도") 
    target_humidity_max = models.FloatField(default=60.0, help_text="에어컨 켜는 습도(%)")
    auto_control_enabled = models.BooleanField(default=False, help_text="자동 제어 활성화")
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"온도: {self.target_temp_max}°C, 습도: {self.target_humidity_max}%"

    @classmethod
    def get_settings(cls):
        """설정 가져오기 (없으면 생성)"""
        settings, created = cls.objects.get_or_create(
            id=1,  # 항상 하나의 설정만 사용
            defaults={
                'target_temp_max': 28.0,
                'target_humidity_max': 60.0,
                'auto_control_enabled': False
            }
        )
        return settings