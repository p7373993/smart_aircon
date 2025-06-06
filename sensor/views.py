from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import PowerUsageLog
from .models import AirconLog
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64

# 한글 폰트 설정
plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 깨짐 방지

def airconlog_chart(request):
    logs = AirconLog.objects.order_by('timestamp')[:100]
    times = [log.timestamp.strftime('%H:%M') for log in logs]
    temps = [log.temperature for log in logs]
    hums = [log.humidity for log in logs]

    plt.figure(figsize=(10,4))
    plt.plot(times, temps, label='온도(°C)', color='red')
    plt.plot(times, hums, label='습도(%)', color='blue')
    plt.title('온습도 변화 그래프')
    plt.xlabel('시간')
    plt.ylabel('값')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return render(request, 'airconlog_chart.html', {'chart': img_base64})

def airconlog_list(request):
    logs = AirconLog.objects.order_by('-timestamp')[:100]
    return render(request, 'airconlog_list.html', {'logs': logs})

@csrf_exempt
def collect_data(request):
    if request.method == 'POST':
        try:
            temperature = float(request.POST.get('temperature'))
            humidity = float(request.POST.get('humidity'))
            AirconLog.objects.create(temperature=temperature, humidity=humidity)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

@csrf_exempt
def collect_power_data(request):
    if request.method == 'POST':
        try:
            watt = float(request.POST.get('watt'))
            energy_kwh = float(request.POST.get('energy_kwh'))
            is_power_on = request.POST.get('is_power_on', 'false').lower() == 'true'
            PowerUsageLog.objects.create(
                watt=watt,
                energy_kwh=energy_kwh,
                is_power_on=is_power_on
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

# 전력 사용량 리스트
def power_usage_list(request):
    logs = PowerUsageLog.objects.order_by('-timestamp')[:100]
    return render(request, 'power_usage_list.html', {'logs': logs})

# 전력 사용량 그래프


def power_usage_chart(request):
    logs = PowerUsageLog.objects.order_by('timestamp')[:100]
    times = [log.timestamp for log in logs]
    watts = [log.watt for log in logs]
    energy = [log.energy_kwh for log in logs]

    plt.figure(figsize=(10,4))
    plt.plot(times, watts, label='Watt')
    plt.plot(times, energy, label='kWh')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return render(request, 'power_usage_chart.html', {'chart': img_base64})

def home(request):
    return HttpResponse("스마트 에어컨 시스템에 오신 것을 환영합니다!")