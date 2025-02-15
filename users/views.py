from django.http import JsonResponse
from django.shortcuts import render, redirect
import secrets
import requests
import json
from django.conf import settings
from django.contrib.auth import login as auth_login
from users.models import User, NeighborRequest, Neighbor, Notification, UserBadge
import urllib.parse
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout
from django.shortcuts import get_list_or_404
from diaries.models import Diary
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from diaries.models import Diary
from django.utils.timezone import now, timedelta
from django.db import transaction
from .forms import UserUpdateForm


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
                return redirect('users:main')    
            else:
                messages.error(request, "비밀번호가 올바르지 않습니다.")  
                return redirect('users:login')  
        except User.DoesNotExist:
            messages.error(request, "존재하지 않는 계정입니다.")
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
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return redirect("users:signup")  

        # ID 중복 확인
        if User.objects.filter(login_id=login_id).exists():
            messages.error(request, "이미 사용 중인 아이디입니다.")
            return redirect("users:signup")  
        
        user = User(login_id=login_id)
        user.set_password(password) 
        user.nickname=make_unique_nickname_of_social_login(login_id)
        user.save()

        messages.success(request, "회원가입이 완료되었습니다!")
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
    return redirect("users:main")  # 로그인 후 이동할 페이지


# 네이버 로그인 페이지로 리디렉션하는 함수
def naver_login(request):
    naver_auth_url = "https://nid.naver.com/oauth2.0/authorize"
    state = secrets.token_urlsafe(16)  # CSRF 보호용 state 값
    request.session['naver_state'] = state

    params = {
        "response_type": "code",
        "client_id": NAVER_CLIENT_ID,
        "redirect_uri": NAVER_REDIRECT_URI,
        "state": state,
        "auth_type": "reauthenticate",  # 🔹 사용자가 네이버 계정을 다시 선택하도록 강제
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
    return redirect('users:main')



def make_unique_nickname_of_social_login(base_nickname):
    import random
    new_nickname = base_nickname
    
    while User.objects.filter(nickname=new_nickname).exists():
        random_suffix = ""
        for i in range(11):
            random_suffix += str(random.randrange(0, 10))

        new_nickname = f"{base_nickname}-{random_suffix}"
        
    return new_nickname



NAVER_LOGOUT_URL = "https://nid.naver.com/nidlogin.logout"

def logout_view(request):
    if request.method == "POST":
        # 네이버 소셜 로그아웃 처리
        access_token = request.session.get("naver_access_token")  
        if access_token:
            delete_token_url = "https://nid.naver.com/oauth2.0/token"
            params = {
                "grant_type": "delete",
                "client_id": NAVER_CLIENT_ID,
                "client_secret": NAVER_CLIENT_SECRET,
                "access_token": access_token,
                "service_provider": "NAVER"
            }
            requests.get(delete_token_url, params=params, timeout=10)  # 네이버 토큰 삭제 요청
        
        # 모든 로그인 세션 삭제
        request.session.flush()
        logout(request)

        # 🔹 네이버 로그인 세션도 삭제하도록 로그아웃 페이지로 이동
        return redirect('users:login')

    return redirect('users:main')

@login_required
def main(request):
    return render(request, 'users/main.html')

@login_required
def profile(request):
    my_friends_count = Neighbor.objects.filter(Q(user1=request.user) | Q(user2=request.user)).count()
    graph = generate_emotion_graph(request.user)  # 감정 그래프 생성
    my_diary_count = Diary.objects.filter(writer=request.user).count()
    my_badges = UserBadge.objects.filter(user=request.user)
    context = {
        "friend_count" : my_friends_count,
        "graph": graph,
        "diary_count": my_diary_count,
        "badges": my_badges
    }
    return render(request, 'users/profile.html', context)


@login_required
def alarm(request):
    alarms = Notification.objects.filter(user=request.user).order_by('-created_at').prefetch_related("tag_notification")
    
    context = {
        "alarms" : alarms,
    }
    
    return render(request, 'users/alarm.html', context)
def alarm_read_ajax(request):
    # 알림 읽음으로 처리
    if request.method == "POST":
        data = json.loads(request.body)
        notification_id = int(data.get("alarm_id"))
        try:
            Notification.objects.filter(id=notification_id, user=request.user).update(is_read=True)
            return JsonResponse({
                    "success": True,
                    "message": "알림을 읽었습니다."
                })
        except:
            return JsonResponse({
                "success": False,
                "message": "존재하지 않는 알림입니다."
            })


# 감정 그래프
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from matplotlib import font_manager, rc

def generate_emotion_graph(user):
    # 1. 같은 날짜 내에서 가장 최근에 작성된 게시물만 가져오기
    recent_diaries = (
        Diary.objects.filter(writer=user)
        .order_by('-date', '-id')  # 날짜 내림차순, ID 내림차순 (최신 다이어리 유지)
    )
    unique_diaries = []
    seen_dates = set()

    for diary in recent_diaries:
        diary_date = diary.date.strftime("%Y-%m-%d")  # 날짜를 문자열로 변환하여 중복 체크
        if diary_date not in seen_dates:
            unique_diaries.append(diary)
            seen_dates.add(diary_date)
        if len(unique_diaries) >= 7:  # 최대 7개까지만
            break

    # 2. 오래된 순으로 정렬
    unique_diaries = sorted(unique_diaries, key=lambda x: x.date)

    # 3. 감정 점수(y축)
    recent_emotion_scores = [diary.emotion for diary in unique_diaries]

    # 4. X축 라벨(날짜)
    x_labels = [diary.date.strftime("%m/%d") for diary in unique_diaries]

    if not recent_emotion_scores:
        x_labels = ["Date"]  # 빈 그래프의 x축 라벨
        recent_emotion_scores = [0]  # y축 값으로 0 추가


    # 그래프 생성
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_facecolor("#FFF9EA")  # 축 배경색
    fig.patch.set_facecolor("#FFF9EA")  # 전체 그래프 배경색
    ax.plot(x_labels, recent_emotion_scores, marker="p", color="#5c6552", linewidth=4, markeredgewidth=2)
    ax.set_xlabel("Date", fontsize=20, color="#5c6552", labelpad=15)
    ax.set_ylabel("Emotion (0~8)", fontsize=20, color="#5c6552", labelpad=15)
    ax.set_ylim(0, 8)  
    ax.grid(False) 
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=18, colors="#5c6552")  
    ax.tick_params(axis="y", labelsize=18, colors="#5c6552")

    # 처음에 데이터가 하나도 없을 때 그래프 비워놓기
    if len(recent_emotion_scores) == 1 and recent_emotion_scores[0] == 0:
        ax.text(0.5, 4, "데이터가 없습니다.", horizontalalignment='center', verticalalignment='center', 
                fontsize=16, color="#5c6552", transform=ax.transAxes)
    fig.tight_layout()

    # 이미지로 변환
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    
    return image_base64


def user_search_ajax(request):
    query = request.GET.get("query", "")  # 검색어를 GET 파라미터로 받음
    results = []
    
    if not query:
        return JsonResponse({"result": results})
        
    if query[0] == '@':
        # 유저검색
        users = User.objects.exclude(login_id=request.user.login_id).filter(nickname__icontains=query[1:])
    else:
        users = User.objects.exclude(login_id=request.user.login_id).filter(nickname__icontains=query)
        
    for user in users:
        friend_status = "신청가능"  # 기본 상태

        if Neighbor.objects.filter(user1=request.user, user2=user).exists() or \
           Neighbor.objects.filter(user1=user, user2=request.user).exists():
            friend_status = "현재 친구"
        elif NeighborRequest.objects.filter(sender=request.user, receiver=user).exists():
            friend_status = "신청 중"

        results.append({
            "login_id": user.login_id,
            "nickname": user.nickname,
            "profile_photo": (str(user.profile_photo)),
            "friend_status": friend_status,
        })
        
    return JsonResponse({"result": results})


##### 친구 신청 관련 Util함수들 #####
def are_neighbors(user_a, user_b):
    """두 유저가 이웃인지 확인"""
    user1, user2 = sorted([user_a, user_b], key=lambda u: u.login_id)
    return Neighbor.objects.filter(user1=user1, user2=user2).exists()

@transaction.atomic
def addUsersToFriend(user1, user2):
    ''' user1과 user2를 이웃으로 만듦. 이미 이웃이었는지는 검사하지 않음 기존의 이웃 요청은 삭제함 '''
    user1, user2 = sorted([user1, user2], key=lambda u: u.login_id)

    Neighbor.objects.get_or_create(
        user1=user1,
        user2=user2
    )
    
    # 친구 요청을 삭제
    NeighborRequest.objects.filter(Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1)).delete()
    
    return user1, user2
##### 끝. 친구 신청 관련 Util함수들 끝. #####

def cancel_friend_request_ajax(request):
    ''' 이웃 신청 취소 '''
    if request.method == "POST":
        data = json.loads(request.body)
        fromUser = request.user
        try:
            toUser = User.objects.exclude(login_id=fromUser.login_id).get(login_id=data.get('to_user_loginid'))
        except:
            return JsonResponse({
                "success": False,
                "message": "올바르지 않은 상대입니다."
            })
        
        if not NeighborRequest.objects.filter(sender=fromUser, receiver=toUser).exists():
            return JsonResponse({
                "success": False,
                "message": "올바르지 않은 상대입니다."
            })       
        
        NeighborRequest.objects.filter(sender=fromUser, receiver=toUser).delete()
        return JsonResponse({
                "success": True,
                "message": "이웃 요청을 취소했습니다."
            })

def send_friend_request_ajax(request):
    ''' 이웃 신청 '''
    # ajax 포스트 요청일 때:
    if request.method == "POST":
        data = json.loads(request.body)
        fromUser = request.user
        try:
            toUser = User.objects.exclude(login_id=fromUser.login_id).get(login_id=data.get('to_user_loginid'))
        except:
            return JsonResponse({
                "success": False,
                "message": "올바르지 않은 상대입니다."
                })
    
        # 이미 이웃인지 검사
        if are_neighbors(fromUser, toUser):
            return JsonResponse({
                "success": False,
                "message": "이미 이웃인 유저입니다."
                })
        
        # 친구가 아닐 떄..
        my_all_requests = NeighborRequest.objects.filter(sender=fromUser)   # 내가 보낸 모든 친구신청들
        my_all_received_requests = NeighborRequest.objects.filter(receiver=fromUser)    # 내가 받은 모든 친구신청들
        # (1) 이미 신청을 보냈거나 받은 유저다.
        if my_all_requests.filter(receiver=toUser).exists():
            ## (1-1) 이미 신청을 보냈다면
            return JsonResponse({
                "success": False,
                "message": "상대방의 수락을 기다리는 중입니다."
                })  
        if my_all_received_requests.filter(sender=toUser).exists():
            ## (1-2) 이미 신청을 받았다면 친구 수락으로 처리.
            addUsersToFriend(fromUser, toUser)
            
            return JsonResponse({
                "success": True,
                "message": f"상대방의 친구 요청을 수락했습니다. @{toUser.nickname}과 친구가 되었습니다."
                })  
                      
        # (2) 그게 아니면 이웃 신청 보낸다.
        newRequest, created = NeighborRequest.objects.get_or_create(
            sender = fromUser,
            receiver = toUser
        )
        if created:
            # (2)번케이스
            return JsonResponse({
                "success": True,
                "message": "성공적으로 이웃 신청을 보냈습니다."
                })
    
    # get요청일때: pass

def reject_friend_request_ajax(request):
    ''' 이웃 신청 거절 '''
    if request.method == "POST":
        data = json.loads(request.body)
        toUser = request.user
        try:
            fromUser = User.objects.get(login_id=data.get('from_user_loginid'))
        except:
            return JsonResponse({
                "success": False,
                "message": "올바르지 않은 상대입니다."
            })
        
        if not NeighborRequest.objects.filter(sender=fromUser, receiver=toUser).exists():
            return JsonResponse({
                "success": False,
                "message": "올바르지 않은 상대입니다."
            })       
        
        NeighborRequest.objects.filter(sender=fromUser, receiver=toUser).delete()
        return JsonResponse({
                "success": True,
                "message": "이웃 요청을 거절했습니다."
            })

#달력에 해당 날짜의 일기 반환
@login_required
def get_diaries_by_date(request, year, month, day):
    """
    특정 날짜에 해당하는 로그인한 유저의 다이어리를 반환.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX 요청 확인
        diaries = Diary.objects.filter(
            writer=request.user,  # 로그인한 유저의 일기만 필터링
            date__year=year,
            date__month=month,
            date__day=day
        ).order_by('-created_at')
        diary_list = [{"id": diary.id, "title": diary.title, "date": diary.date.strftime("%Y-%m-%d")} for diary in diaries]
        return JsonResponse(diary_list, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def get_today_diaries(request):
    """ 오늘 작성한 로그인한 유저의 일기 반환 """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        today = now().date()
        diaries = Diary.objects.filter(writer=request.user, date=today).order_by('-created_at')
        diary_list = [{"id": diary.id, "title": diary.title, "date": diary.date.strftime("%Y-%m-%d")} for diary in diaries]
        return JsonResponse(diary_list, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def get_last_week_diaries(request):
    """ 최근 7일간 로그인한 유저가 작성한 일기 반환 """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        today = now().date()
        last_week = today - timedelta(days=6)  # 최근 7일(오늘 포함)
        diaries = Diary.objects.filter(writer=request.user, date__range=[last_week, today]).order_by('-date')
        diary_list = [{"id": diary.id, "title": diary.title, "date": diary.date.strftime("%Y-%m-%d")} for diary in diaries]
        return JsonResponse(diary_list, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def update_profile_photo(request):
    if request.method == "POST" and request.FILES.get("profile_photo"):
        user = request.user
        user.profile_photo = request.FILES["profile_photo"]
        user.save()
        
        messages.success(request, "프로필 사진이 성공적으로 변경되었습니다!")
        return redirect("users:profile")  
    
    messages.error(request, "바꿀 프로필 사진을 선택하지 않았습니다.")
    return redirect("users:profile")


# profile_edit에서 사진 바꾸면 profile_edit 페이지로 redirect되도록 따로 만든 함수(프로필 페이지에서 바꾸면 프로필 페이지로 가는 함수 따로 있음)
@login_required
def update_profile_photo_edit(request):
    if request.method == "POST" and request.FILES.get("profile_photo"):
        user = request.user
        user.profile_photo = request.FILES.get("profile_photo")
        user.save()
        
        messages.success(request, "프로필 사진이 성공적으로 변경되었습니다!")
        return redirect("users:profile_edit")  
    
    messages.error(request, "바꿀 프로필 사진을 선택하지 않았습니다.")
    return redirect("users:profile_edit")

def profile_edit(request):
    user = request.user

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user) # 기존 정보 불러오기
        if form.is_valid():
            form.save()
            return redirect("users:profile") # 수정하고 profile로 redirect, 향후에 바꿀거면 바꾸세용
        
        # 닉네임 중복 오류 메시지
        else:
            if "nickname" in form.errors:
                messages.error(request, "이미 사용 중인 닉네임입니다.")
        
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'users/profile_edit.html', {"form":form})


@login_required
def friend_check(request):
    neighbors = Neighbor.objects.filter(Q(user1=request.user) | Q(user2=request.user))

    # 이웃 정보를 리스트로 변환
    friends = []
    for neighbor in neighbors:
        if neighbor.user1 == request.user:
            friend = neighbor.user2  # user1이 본인이면 상대방(user2)을 이웃으로
        else:
            friend = neighbor.user1  # user2가 본인이면 상대방(user1)을 이웃으로
        
        friends.append({
            "nickname": friend.nickname,
            "profile_photo": friend.profile_photo.url if friend.profile_photo else None,
            "introduce": friend.introduce if friend.introduce else " ",
        })

    context = {
        "friends": friends,
        "friend_count": len(friends),
    }
    return render(request, 'users/friend_check.html', context)