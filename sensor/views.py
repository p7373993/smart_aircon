from datetime import timezone
from time import localtime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import AirconUsageLog, PowerUsageLog, AirconLog, UserAirconSettings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import io, base64
from django.utils import timezone
import pandas as pd
from datetime import timedelta
import requests
from django.views.decorators.http import require_http_methods

# 한글 폰트 설정 (확실한 방법)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import io, base64
from django.utils import timezone
import pandas as pd
from datetime import timedelta
import requests
from django.views.decorators.http import require_http_methods

# Windows 한글 폰트 강제 설정
try:
    # 시스템에서 사용 가능한 한글 폰트 찾기
    font_list = [f.name for f in fm.fontManager.ttflist]
    
    if 'Malgun Gothic' in font_list:
        plt.rcParams['font.family'] = 'Malgun Gothic'
    elif 'NanumGothic' in font_list:
        plt.rcParams['font.family'] = 'NanumGothic'
    elif 'AppleGothic' in font_list:
        plt.rcParams['font.family'] = 'AppleGothic'
    else:
        # 한글 폰트가 없으면 영어로 표시
        plt.rcParams['font.family'] = 'DejaVu Sans'
        print("한글 폰트를 찾을 수 없어 영어로 표시됩니다.")
except:
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 깨짐 방지

def airconlog_chart(request):
    # 최신 데이터 100개를 가져온 후 리스트로 변환하여 역순으로 정렬
    logs = list(AirconLog.objects.order_by('-timestamp')[:100])[::-1]
    
    # 데이터가 없는 경우 처리
    if not logs:
        return render(request, 'airconlog_chart.html', {'chart': None, 'message': '데이터가 없습니다.'})
    
    times = [timezone.localtime(log.timestamp).strftime('%H:%M') for log in logs]
    temps = [log.temperature for log in logs]
    hums = [log.humidity for log in logs]

    # 그래프 스타일 개선
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('white')
    
    # 온도 라인 (빨간색)
    temp_line = ax.plot(times, temps, linewidth=3, color='#ff6b6b', 
                       label='Temperature(°C)', marker='o', markersize=4, 
                       markerfacecolor='#ff5252', markeredgecolor='white', markeredgewidth=1)
    
    # 습도 라인 (파란색) 
    hum_line = ax.plot(times, hums, linewidth=3, color='#4dabf7',
                      label='Humidity(%)', marker='s', markersize=4,
                      markerfacecolor='#339af0', markeredgecolor='white', markeredgewidth=1)
    
    # 배경 영역 채우기
    ax.fill_between(times, temps, alpha=0.2, color='#ff6b6b')
    ax.fill_between(times, hums, alpha=0.2, color='#4dabf7')
    
    # 그리드 스타일
    ax.grid(True, linestyle='--', alpha=0.7, color='#dee2e6')
    ax.set_axisbelow(True)
    
    # 제목과 레이블 (이모지 제거)
    ax.set_title('Indoor Temperature & Humidity Monitor', fontsize=18, fontweight='bold', 
                color='#343a40', pad=20)
    ax.set_xlabel('Time', fontsize=12, fontweight='bold', color='#495057')
    ax.set_ylabel('Value', fontsize=12, fontweight='bold', color='#495057')
    
    # 범례 스타일링
    legend = ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True,
                      fontsize=11, framealpha=0.9)
    legend.get_frame().set_facecolor('#f8f9fa')
    legend.get_frame().set_edgecolor('#dee2e6')
    
    # x축 레이블 회전 및 간격 조정
    plt.xticks(rotation=45, fontsize=9)
    plt.yticks(fontsize=10)
    
    # 여백 조정
    plt.tight_layout()
    
    # 테두리 스타일
    for spine in ax.spines.values():
        spine.set_edgecolor('#dee2e6')
        spine.set_linewidth(1.5)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
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

def power_usage_list(request):
    logs = PowerUsageLog.objects.order_by('-timestamp')[:100]
    return render(request, 'power_usage_list.html', {'logs': logs})

def power_usage_chart(request):
    logs = PowerUsageLog.objects.order_by('timestamp')[:100]
    
    if not logs:
        return render(request, 'power_usage_chart.html', {'chart': None})
    
    times = [log.timestamp for log in logs]
    watts = [log.watt for log in logs]
    energy = [log.energy_kwh for log in logs]

    # 그래프 스타일 개선
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.patch.set_facecolor('white')
    
    # 전력 소비량 그래프 (이모지 제거)
    ax1.plot(times, watts, linewidth=3, color='#ff8a80', marker='o', 
            markersize=3, label='Real-time Power(W)')
    ax1.fill_between(times, watts, alpha=0.3, color='#ff8a80')
    ax1.set_title('Power Usage Monitoring', fontsize=16, fontweight='bold', 
                 color='#343a40', pad=15)
    ax1.set_ylabel('Power (W)', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()
    
    # 누적 에너지 그래프 (이모지 제거)
    ax2.plot(times, energy, linewidth=3, color='#69f0ae', marker='s',
            markersize=3, label='Cumulative Energy(kWh)')
    ax2.fill_between(times, energy, alpha=0.3, color='#69f0ae')
    ax2.set_title('Cumulative Energy Usage', fontsize=16, fontweight='bold',
                 color='#343a40', pad=15)
    ax2.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Energy (kWh)', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()
    
    # x축 포맷 개선
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return render(request, 'power_usage_chart.html', {'chart': img_base64})

def latest_airconlog(request):
    # 가장 최근의 에어컨 사용 로그
    latest_usage = AirconUsageLog.objects.order_by('-timestamp').first()
    # 가장 최근의 온습도 로그 (옵션)
    latest_env = AirconLog.objects.order_by('-timestamp').first()
    data = {
        'temperature': latest_env.temperature if latest_env else 'N/A',
        'humidity': latest_env.humidity if latest_env else 'N/A',
        'ac_status': '가동중' if (latest_usage and latest_usage.is_aircon_on) else '대기중'
    }
    return JsonResponse(data)

def log_aircon_usage(is_on):
    AirconUsageLog.objects.create(is_aircon_on=is_on)

def aircon_usage_chart(request):
    # 오늘 0시~지금까지의 로그만 조회
    now = timezone.localtime()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    logs = AirconUsageLog.objects.filter(timestamp__gte=today_start).order_by('timestamp')
    # now = timezone.localtime()
    # today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # yesterday_start = today_start - timedelta(days=1)  # 어제 0시
    # yesterday_end = today_start - timedelta(seconds=1)  # 어제 23:59:59
    # logs = AirconUsageLog.objects.filter(
    #     timestamp__gte=yesterday_start,
    #     timestamp__lte=yesterday_end
    # ).order_by('timestamp')
    if not logs:
        img_base64 = ""
    else:
        # 로그를 DataFrame으로 변환
        df = pd.DataFrame(list(logs.values('timestamp', 'is_aircon_on')))
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # # 30분 단위 구간 생성 (48개 구간)
        bins = [today_start + timedelta(minutes=30*i) for i in range(49)]
        labels = [(today_start + timedelta(minutes=30*i)).strftime("%H:%M") for i in range(48)]
        # bins = [yesterday_start + timedelta(minutes=30*i) for i in range(49)]
        # labels = [(yesterday_start + timedelta(minutes=30*i)).strftime("%H:%M") for i in range(48)]
        # 각 로그 구간별로 켜져 있던 시간(분) 누적
        usage_per_bin = [0]*48
        for i in range(len(df)-1):
            start = df.iloc[i]['timestamp']
            end = df.iloc[i+1]['timestamp']
            state = df.iloc[i]['is_aircon_on']
            if state:  # 켜져있던 구간만 계산
                # 구간별로 겹치는 시간만큼 누적
                for b in range(48):
                    bin_start = bins[b]
                    bin_end = bins[b+1]
                    overlap_start = max(start, bin_start)
                    overlap_end = min(end, bin_end)
                    overlap = (overlap_end - overlap_start).total_seconds() / 60
                    if overlap > 0:
                        usage_per_bin[b] += overlap
        
        # 마지막 로그가 ON이면 현재까지 누적
        if len(df) > 0 and df.iloc[-1]['is_aircon_on']:
            start = df.iloc[-1]['timestamp']
            end = now
            for b in range(48):
                bin_start = bins[b]
                bin_end = bins[b+1]
                overlap_start = max(start, bin_start)
                overlap_end = min(end, bin_end)
                overlap = (overlap_end - overlap_start).total_seconds() / 60
                if overlap > 0:
                    usage_per_bin[b] += overlap

        # 그래프 스타일 개선
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(20, 7))
        fig.patch.set_facecolor('white')
        
        # 색상 배열 생성 (그라데이션 효과)
        colors = []
        for value in usage_per_bin:
            if value == 0:
                colors.append('#e9ecef')  # 회색 (사용 안 함)
            elif value <= 10:
                colors.append('#74c0fc')  # 연한 파랑 (적은 사용)
            elif value <= 20:
                colors.append('#339af0')  # 중간 파랑
            else:
                colors.append('#1c7ed6')  # 진한 파랑 (많은 사용)
        
        # 막대 그래프 그리기
        bars = ax.bar(range(len(labels)), usage_per_bin, color=colors, 
                     edgecolor='white', linewidth=1.5, alpha=0.8)
        
        # 값 표시 (10분 이상인 경우에만)
        for i, (bar, value) in enumerate(zip(bars, usage_per_bin)):
            if value >= 10:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                       f'{int(value)}min', ha='center', va='bottom', 
                       fontsize=8, fontweight='bold', color='#495057')
        
        # 그리드 스타일
        ax.grid(True, axis='y', linestyle='--', alpha=0.7, color='#dee2e6')
        ax.set_axisbelow(True)
        
        # 제목과 레이블 
        ax.set_title('Daily AC Usage Analysis (30min intervals)', fontsize=20, 
                    fontweight='bold', color='#343a40', pad=25)
        ax.set_xlabel('Time Period', fontsize=14, fontweight='bold', color='#495057')
        ax.set_ylabel('Usage Time (min)', fontsize=14, fontweight='bold', color='#495057')
        
        # x축 설정
        ax.set_xticks(range(0, len(labels), 4))  # 2시간 간격으로 표시
        ax.set_xticklabels([labels[i] for i in range(0, len(labels), 4)], 
                          rotation=0, fontsize=11)
        
        # y축 설정
        ax.set_ylim(0, max(usage_per_bin) * 1.1 if max(usage_per_bin) > 0 else 30)
        plt.yticks(fontsize=11)
        
        # 총 사용시간 표시 (이모지 제거)
        total_usage = sum(usage_per_bin)
        ax.text(0.02, 0.98, f'Total Usage: {int(total_usage)}min ({total_usage/60:.1f}h)', 
                transform=ax.transAxes, fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#e3f2fd', alpha=0.8),
                verticalalignment='top')
        
        # 범례를 영어로 변경
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='#e9ecef', label='Not Used'),
            plt.Rectangle((0,0),1,1, facecolor='#74c0fc', label='1-10min'),
            plt.Rectangle((0,0),1,1, facecolor='#339af0', label='11-20min'),
            plt.Rectangle((0,0),1,1, facecolor='#1c7ed6', label='21min+')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True, 
                 fancybox=True, shadow=True, fontsize=10)
        
        # 테두리 스타일
        for spine in ax.spines.values():
            spine.set_edgecolor('#dee2e6')
            spine.set_linewidth(1.5)
        
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return render(request, 'aircon_usage_chart.html', {'chart': img_base64})

# 자동 제어 관련 함수들
def get_user_settings(request):
    """사용자 설정 가져오기 API"""
    try:
        settings = UserAirconSettings.get_settings()
        data = {
            'target_temp_max': settings.target_temp_max,
            'target_humidity_max': settings.target_humidity_max,
            'auto_control_enabled': settings.auto_control_enabled,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt 
@require_http_methods(["POST"])
def update_user_settings(request):
    """사용자 설정 업데이트"""
    try:
        settings = UserAirconSettings.get_settings()
        
        # POST 데이터에서 값 가져오기
        settings.target_temp_max = float(request.POST.get('target_temp_max', settings.target_temp_max))
        settings.target_humidity_max = float(request.POST.get('target_humidity_max', settings.target_humidity_max))
        settings.auto_control_enabled = request.POST.get('auto_control_enabled', 'false').lower() == 'true'
        
        # 유효성 검사
        if not (15 <= settings.target_temp_max <= 35):
            return JsonResponse({'status': 'error', 'message': '온도는 15~35도 사이여야 합니다.'})
            
        if not (30 <= settings.target_humidity_max <= 90):
            return JsonResponse({'status': 'error', 'message': '습도는 30~90% 사이여야 합니다.'})
        
        settings.save()
        return JsonResponse({'status': 'success', 'message': '설정이 저장되었습니다.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def check_and_control_aircon():
    """자동 제어 로직 실행 함수 - 온도 28도 OR 습도 60% 이상이면 켜기"""
    try:
        # 사용자 설정 가져오기
        settings = UserAirconSettings.get_settings()
        
        if not settings.auto_control_enabled:
            return {'status': 'disabled', 'message': '자동 제어가 비활성화되어 있습니다.'}
        
        # 최신 온습도 데이터 가져오기
        latest_log = AirconLog.objects.order_by('-timestamp').first()
        if not latest_log:
            return {'status': 'error', 'message': '온습도 데이터가 없습니다.'}
        
        current_temp = latest_log.temperature
        current_humidity = latest_log.humidity
        
        # 현재 에어컨 상태 확인
        latest_usage = AirconUsageLog.objects.order_by('-timestamp').first()
        current_ac_status = latest_usage.is_aircon_on if latest_usage else False
        
        # 제어 로직: 온도 OR 습도 조건
        should_turn_on = (current_temp >= settings.target_temp_max) or (current_humidity >= settings.target_humidity_max)
        
        # 상태 변경이 필요한 경우에만 제어
        if should_turn_on != current_ac_status:
            action = 'on' if should_turn_on else 'off'
            
            # 라즈베리파이에 제어 명령 전송
            url = 'http://192.168.0.71:5000/aircon'
            try:
                response = requests.post(url, json={'action': action}, timeout=3)
                
                # 에어컨 사용 로그 저장
                AirconUsageLog.objects.create(is_aircon_on=should_turn_on)
                
                return {
                    'status': 'success', 
                    'action': action,
                    'message': f'에어컨을 자동으로 {"켰습니다" if should_turn_on else "껐습니다"}',
                    'reason': f'온도: {current_temp}°C, 습도: {current_humidity}%',
                    'current_temp': current_temp,
                    'current_humidity': current_humidity
                }
                
            except Exception as e:
                return {'status': 'error', 'message': f'에어컨 제어 실패: {str(e)}'}
        else:
            return {
                'status': 'no_change', 
                'message': '현재 상태 유지',
                'current_temp': current_temp,
                'current_humidity': current_humidity
            }
            
    except Exception as e:
        return {'status': 'error', 'message': f'자동 제어 오류: {str(e)}'}

@csrf_exempt
def manual_auto_control(request):
    """수동으로 자동 제어 로직 실행"""
    if request.method == 'POST':
        result = check_and_control_aircon()
        return JsonResponse(result)
    return JsonResponse({'status': 'error', 'message': 'POST만 지원'})

def home(request):
    latest_log = AirconLog.objects.order_by('-timestamp').first()
    latest_usage = AirconUsageLog.objects.order_by('-timestamp').first()
    try:
        settings = UserAirconSettings.get_settings()
    except:
        settings = None
    
    context = {
        'current_temp': latest_log.temperature if latest_log else 'N/A',
        'current_humidity': latest_log.humidity if latest_log else 'N/A',
        'ac_status': '가동중' if (latest_usage and latest_usage.is_aircon_on) else '대기중',
        'settings': settings
    }
    return render(request, 'main.html', context)