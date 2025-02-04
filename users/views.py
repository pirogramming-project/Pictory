from django.shortcuts import render, redirect
import secrets
import requests
from django.conf import settings
from django.contrib.auth import login as auth_login
from users.models import User
import urllib.parse
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout

KAKAO_CLIENT_ID = settings.KAKAO_CLIENT_ID
KAKAO_REDIRECT_URI = settings.KAKAO_REDIRECT_URI

NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET
NAVER_REDIRECT_URI = settings.NAVER_REDIRECT_URI

def login_view(request):
    if request.method == "POST":
        login_id = request.POST['login_id']
        input_password = request.POST['password']
        try:
            user = User.objects.get(login_id=login_id)  
            if check_password(input_password, user.password):  
                auth_login(request, user)
                return redirect('users:main')    # 메인 페이지로 이동 (미구현)
            else:
                print("잘못된 비밀번호")
                return redirect('users:login')
        except User.DoesNotExist:
            print("사용자를 찾을 수 없습니다.")
            return redirect('users:login')
    
    # 만약에 유저가 로그인했다
    if request.user.is_authenticated:
        return redirect('users:main')
    
    # 아니다
    return render(request, 'users/login.html')

def signup(request):
    if request.method == "POST":
        login_id = request.POST.get("login_id")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
  
        # 비밀번호 확인
        if password != password_confirm:
            return redirect("users:signup")  

        # ID 중복 확인
        if User.objects.filter(login_id=login_id).exists():
            return redirect("users:signup")  
        
        user = User(login_id=login_id)
        user.set_password(password) 
        user.nickname=make_unique_nickname_of_social_login(login_id)
        user.save()
        
        return redirect("users:login")
    return render(request, "users/signup.html")
         


def kakao_login(request):
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?response_type=code"
        f"&client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}"
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
            "client_id": KAKAO_CLIENT_ID,
            "redirect_uri": KAKAO_REDIRECT_URI,
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

    if created:
        # 랜덤 비밀번호 생성 및 설정
        random_password = secrets.token_urlsafe(32)  # 랜덤 비밀번호 생성 (32자리)
        user.set_password(random_password)  # 비밀번호 설정
        user.save()

    #로그인 처리
    auth_login(request, user)
    #main페이지 생기면 거기로 주소 바뀔 예정
    return redirect('/')



def make_unique_nickname_of_social_login(base_nickname):
    import random
    new_nickname = base_nickname
    
    while User.objects.filter(nickname=new_nickname).exists():
        random_suffix = ""
        for i in range(11):
            random_suffix += str(random.randrange(0, 10))

        new_nickname = f"{base_nickname}-{random_suffix}"
        
    return new_nickname

# 로그아웃
def logout_view(request):
    if request.method == "POST":
        logout(request)

    return redirect('/')

  
def main(request):
    return render(request, 'users/main.html')

def profile(request):
    return render(request, 'users/profile.html')

def alarm(request):
    return render(request, 'users/alarm.html')


# 감정 그래프
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render

def generate_emotion_graph():
    """ 최근 7일 감정 그래프를 생성하고 Base64로 변환하는 함수 """
    # 최근 7개의 감정 점수를 DB에서 가져오는 예제 (ORM을 사용하는 것이 일반적)
    recent_emotion_scores = [2, 7, 6, 3, 7, 6, 1]
    dates = ["1/25", "1/26", "1/27", "1/28", "1/29", "1/30", "1/31"]

    # 그래프 생성
    plt.rcParams["font.family"] = "Malgun Gothic"
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(dates, recent_emotion_scores, marker="o", linestyle="-", color="b", linewidth=2)
    ax.set_xlabel("날짜", fontsize=12)
    ax.set_ylabel("감정 점수 (0~8)", fontsize=12)
    ax.set_ylim(0, 8)  # 감정 점수 범위 설정
    ax.grid(False) 
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 이미지를 Base64로 변환
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    
    return image_base64

def profile(request):
    """ 프로필 페이지 뷰 """
    graph = generate_emotion_graph()  # 감정 그래프 생성

    return render(request, "users/profile.html", {"graph": graph})

