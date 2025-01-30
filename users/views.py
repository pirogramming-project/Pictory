from django.shortcuts import render, redirect
import secrets
import requests
from django.conf import settings
from django.contrib.auth import login as auth_login
from users.models import User
import urllib.parse


NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET
NAVER_REDIRECT_URI = settings.NAVER_REDIRECT_URI

def login_view(request):
    if request.method == "POST":
        pass
    
    return render(request, 'users/login.html')


def kakao_login(request):
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?response_type=code"
        f"&client_id={settings.KAKAO_CLIENT_ID}&redirect_uri={settings.KAKAO_REDIRECT_URI}"
        f"&prompt=login"
    )
    return redirect(kakao_auth_url)

def kakao_callback(request):
    """카카오 로그인 콜백"""
    code = request.GET.get("code")

    # 1. Authorization Code를 사용하여 Access Token 요청
    token_request = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        },
    )
    token_json = token_request.json()
    access_token = token_json.get("access_token")

    # 2. Access Token을 사용하여 유저 정보 요청
    user_info_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info = user_info_request.json()

    kakao_id = user_info["id"]
    login_id = f'kakao_{kakao_id}'
    nickname = user_info["properties"]['nickname']
    

    # 3. Custom User Model에서 해당 유저가 존재하는지 확인
    user, created = User.objects.get_or_create(login_id=login_id)

    if created:
        # 4. 새 유저라면 추가 정보 저장
        user.login_id = login_id  # 유저네임을 카카오 ID 기반으로 설정
        user.nickname = make_unique_nickname_of_social_login(nickname)
        random_password = secrets.token_urlsafe(32)  # 일반 로그인 방지용 랜덤 문자열 생성
        user.set_password(random_password)  # 비밀번호 설정
        user.save()

    # 5. 로그인 처리
    auth_login(request, user)
    return redirect("/")  # 로그인 후 이동할 페이지



def signup(request):
    if request.method == "POST":
        pass
    
    
    return render(request, 'users/signup.html')


# 네이버 로그인 페이지로 리디렉션하는 함수
def naver_login(request):
    naver_auth_url = "https://nid.naver.com/oauth2.0/authorize"
    state = secrets.token_urlsafe(16) # 보안 관련
    request.session['naver_state'] = state

    params = {
        "response_type": "code",
        "client_id": NAVER_CLIENT_ID,
        "redirect_uri": NAVER_REDIRECT_URI,
        "state": state,
    }
    url = f"{naver_auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(url)

# 네이버 로그인하고 콜백하는 함수
def naver_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    session_state = request.session.get('naver_state')
    
    #오류 잡는 부분들
    if state != session_state:
        return render(request, "users/login.html", {"error": "CSRF 검증 실패"})

    token_url = "https://nid.naver.com/oauth2.0/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": NAVER_CLIENT_ID,
        "client_secret": NAVER_CLIENT_SECRET,
        "code": code,
        "state": state,
    }

    response = requests.get(token_url, params=params, timeout=10)
    if response.status_code != 200:
        return render(request, "users/login.html", {"error": "네이버 로그인 실패: 네이버 서버 오류"})

    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return render(request, "users/login.html", {"error": "네이버 로그인 실패: access token 발급 오류"})
    # 여기까지 오류 잡는 부분

    # 네이버 사용자 정보 가져오기
    user_info = get_naver_user_info(access_token)
    return handle_naver_user(request, user_info)


# 사용자 정보 가져오기 (위에서 사용하는 함수)
def get_naver_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers, timeout=10)

    if response.status_code != 200:
        raise Exception("네이버 사용자 정보 요청 실패")

    user_data = response.json()
    if user_data.get("resultcode") != "00":
        raise Exception(f"네이버 사용자 정보 요청 실패: {user_data.get('message')}")

    return user_data["response"]

def handle_naver_user(request, user_info):
    email = user_info.get("email")
    nickname = user_info.get("nickname")

    if not email:
        return render(request, "users/login.html", {"error": "네이버 계정에 이메일이 없습니다."})

    user, created = User.objects.get_or_create(email=email, defaults={"nickname": make_unique_nickname_of_social_login(nickname), "login_id": email})

    #로그인 처리
    auth_login(request, user)
    #main페이지 생기면 거기로 주소 바뀔 예정
    return redirect('/')



def make_unique_nickname_of_social_login(base_nickname):
    import random
    import string
    new_nickname = base_nickname
    
    while User.objects.filter(nickname=new_nickname).exists():
        random_suffix = "".join(random.choices(string.ascii_lowercase, k=3))
        new_nickname = f"{base_nickname}{random_suffix}"
        
    return new_nickname
