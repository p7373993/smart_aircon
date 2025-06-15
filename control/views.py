import traceback
from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from sensor.models import AirconUsageLog

@csrf_exempt
def remote_aircon_control(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        url = 'http://192.168.0.71:5000/aircon'
        try:
            response = requests.post(url, json={'action': action}, timeout=3)
            # 에어컨 사용 로그 저장
            try:
                if action == 'on':
                    AirconUsageLog.objects.create(is_aircon_on=True)
                elif action == 'off':
                    AirconUsageLog.objects.create(is_aircon_on=False)
            except Exception as log_err:
                # 로그 저장 중 에러 발생 시
                return JsonResponse({'status': 'error', 'message': f'로그 저장 실패: {log_err}'}, status=500)
            # 응답이 JSON이 아닐 수 있으니 방어
            try:
                return JsonResponse(response.json())
            except Exception as json_err:
                return JsonResponse({'status': 'error', 'message': f'라즈베리파이 응답 JSON 파싱 실패: {json_err}'}, status=500)
        except Exception as e:
            # 전체 예외 메시지와 스택 트레이스를 함께 반환(개발용)
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            return JsonResponse({'status': 'error', 'message': error_msg}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST만 지원'})