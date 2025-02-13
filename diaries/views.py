from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Diary, Frame, Tag, User_Tag, User
from users.models import Neighbor
from django.contrib.auth.decorators import login_required
from .forms import DiaryForm
from datetime import date, datetime
from django.urls import reverse
from django.core.files.base import ContentFile
import base64
from django.http import Http404, JsonResponse
from django.db.models import Q
from django.db import transaction
import json
import os

KAKAO_APPKEY_JS = settings.KAKAO_APPKEY_JS

# 디테일 페이지
@login_required
def diary_detail(request, diary_id):
    diary = get_object_or_404(Diary, id=diary_id)  
    user_tags = User_Tag.objects.filter(diary=diary)  
    photo = diary.four_cut_photo.image_file

    # 감정 점수와 SVG 매핑 가져오기
    from .forms import EMOTION_CHOICES
    emotion_svg = dict(EMOTION_CHOICES).get(diary.emotion, '')

    # 날씨 SVG 매핑 가져오기
    from .forms import WEATHER_CHOICES 
    weather_svg = dict(WEATHER_CHOICES).get(diary.weather, '')

    if diary.writer != request.user:
        raise Http404("페이지 접근 권한이 없습니다.")  
    
    context = {
        'diary': diary,
        'user_tags': user_tags,
        'photo' : photo,
        'emotion_svg': emotion_svg,
        'weather_svg': weather_svg,
    }
    return render(request, 'diaries/detail.html', context)

@login_required
def diaries_by_date(request, year, month, day):
    # 로그인한 유저가 작성한 특정 날짜의 다이어리 조회
    selected_date = datetime(year, month, day)
    diaries = Diary.objects.filter(writer=request.user, date=selected_date)

    if not diaries.exists():
        return render(request, 'diaries/no_diary.html', {'selected_date': selected_date})

    # 다이어리가 하나인 경우 바로 디테일 페이지로 이동
    if diaries.count() == 1:
        return redirect('diaries:diary_detail', diary_id=diaries.first().id)

    # 여러 다이어리가 있는 경우 선택 화면으로 이동
    return render(request, 'diaries/diary_list.html', {'diaries': diaries, 'selected_date': selected_date})

# 다이어리 수정
@login_required
@transaction.atomic
def edit_diary(request, diary_id):
    diary = get_object_or_404(Diary, id=diary_id)

    if diary.writer != request.user:
        raise Http404("존재하지 않는 페이지입니다.")  
    
    neighbors = User.objects.filter(
        Q(neighbors1__user2=request.user) | Q(neighbors2__user1=request.user)
    ).exclude(login_id=request.user.login_id).distinct()

    if request.method == 'POST':
        form = DiaryForm(request.POST, instance=diary)

        if form.is_valid():
            diary = form.save(commit=False)
            diary.place_address = request.POST.get('place_address')
            diary.save()
            form.save_m2m()

            # 기존 태그 삭제 후 새 태그 저장
            Tag.objects.filter(diary=diary).delete()  # 기존 태그 삭제
            ## 새로운 태그 추가
            raw_tag_string = request.POST['create_diary_post']
            raw_tags = raw_tag_string.split('#')
            tags = set([])
            for raw_tag in raw_tags:
                tag = raw_tag.strip()
                if tag:
                    tags.add(tag)
            for tag in tags:
                Tag.objects.create(
                    diary = diary,
                    name = tag
                )

            # 기존 유저 태그 삭제 후 새 태그 저장
            diary.user_tags.set(form.cleaned_data["user_tags"])
            
            return redirect(reverse('diaries:diary_detail', kwargs={'diary_id': diary.id}))


        else:
            print("폼 유효성 검사 실패:", form.errors)  # 에러 확인용

    else:
        form = DiaryForm(instance=diary)

    #all_users = User.objects.all()
    user_tags = diary.user_tags.all()
    diary_tags = diary.tags.all()

    context = {
        'form': form,
        'diary': diary,
        # 'all_users': all_users,
        'neighbors':neighbors, #이웃들만
        'user_tags': user_tags, #create에서 태그했던 이웃들들
        'diary_tags': diary_tags,
        "KAKAO_MAP_APPKEY_JS":KAKAO_APPKEY_JS
    }
    return render(request, 'diaries/edit_diary.html', context)


# 다이어리 삭제
@login_required
def delete_diary(request, diary_id):
    diary = get_object_or_404(Diary, id=diary_id)
    if request.method == "POST":
        diary.delete()
        return redirect('diaries:mydiaries')  
    return redirect('diaries:diary_detail', diary_id=diary_id)

# 인생네컷 추가 페이지1
def select_photo_type(request):
    return render(request, 'diaries/photo_type.html')
  
# 인생네컷 추가 페이지2
def select_frame(request):
    return render(request, 'diaries/frame_select.html')
  
# 인생네컷 추가 페이지3
@login_required
@transaction.atomic
def custom_photo(request, frame_type):
    if request.method == "POST":
        '''사진 관련 데이터 몽땅 저장하고 다음 페이지로 이동 '''
        # 1. 사진 프레임 저장
        saved_photo = request.POST.get("saved_photo") # 최종 이미지

        created_frame = None
        if saved_photo:
            format, imgstr = saved_photo.split(";base64,")  # Base64 데이터(saved_photo) 분리
            ext = format.split("/")[-1]  # 확장자 추출 (png, jpg 등)
            img_file = ContentFile(base64.b64decode(imgstr), name=f"frame.{ext}")   # Base64 디코딩하여 파일로 변환
            created_frame = Frame.objects.create(image_file=img_file)
            if not created_frame:
                print("[프레임]저장실패.. 다시시도")
                return render(request, 'diaries/custom_photo.html')
                     
        # 저장 성공 시 리다이렉트
        if created_frame:
            return redirect("diaries:create_diary", created_frame.id)
        
        print("저장실패.. 다시시도?")
    
    
    """static 폴더에서 stickers 이미지 목록을 가져와 템플릿에 전달"""
    sticker_path = os.path.join(settings.STATICFILES_DIRS[0], "images/stickers")
    # 스티커 폴더 내의 파일 목록 가져오기
    try:
        sticker_files = [f for f in os.listdir(sticker_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    except FileNotFoundError:
        sticker_files = []
    context = {
        'frame_option' : str(frame_type),
        'sticker_files' : sticker_files,
    }
    return render(request, 'diaries/custom_photo.html', context)


# 인생네컷 추가 페이지4
@login_required
@transaction.atomic
def create_diary(request, related_frame_id):
    related_frame = Frame.objects.get(id=related_frame_id)
    # 로그인한 유저의 이웃 관계 필터링
    neighbors = User.objects.filter(
        Q(neighbors1__user2=request.user) | Q(neighbors2__user1=request.user)
    ).exclude(login_id=request.user.login_id).distinct()

    if request.method == 'POST':
        four_cut_photo = related_frame
        
        form = DiaryForm(request.POST)
        if form.is_valid():
            diary = form.save(commit=False) # 유저태그 빼고 저장
            if not diary.date:
                diary.date = date.today()  # 일기 날짜가 입력되지 않았으면 오늘 날짜로 설정
                
            # diary의 다른 필드들 추가하고 diary 먼저 저장.
            diary.writer = request.user
            diary.four_cut_photo = four_cut_photo
            diary.place_address = request.POST.get('place_address')
            diary.save()
            
            ### 일반 태그 처리 및 저장
            raw_tag_string = request.POST['create_diary_post']
            raw_tags = raw_tag_string.split('#')
            tags = set([])
            for raw_tag in raw_tags:
                tag = raw_tag.strip()
                if tag:
                    tags.add(tag)   # tag가 empty string이 아닐 때 셋에 주가
            for tag in tags:
                Tag.objects.create(
                    diary = diary,
                    name = tag
                )

            # diary와 관련된 M2M 필드 저장 (user_tag)
            form.save_m2m()
            

            return redirect(reverse('diaries:diary_detail', kwargs={'diary_id': diary.id}))    
        else:
            print("error: form is not valid")
            related_frame.delete()
            return redirect('diaries:create_diary')
        
    form = DiaryForm()
    context = {
        'form' : form,
        'related_frame_id' : related_frame_id,
        'related_frame_img' : related_frame.image_file,
        'KAKAO_MAP_APPKEY_JS' : KAKAO_APPKEY_JS,
        'neighbors':neighbors,
    }
    return render(request, 'diaries/create_diary.html', context)


@login_required
def community(request):
    myNeightbors = Neighbor.objects.filter(Q(user1=request.user) | Q(user2=request.user)).select_related("user1", "user2")

    friendDiaryList = []
    
    for neighbor in myNeightbors:
        user1 = neighbor.user1
        user2 = neighbor.user2
        if user1 != request.user:
            friendDiaryList.extend(Diary.objects.filter(writer=user1))
        else:
            friendDiaryList.extend(Diary.objects.filter(writer=user2))
            
    context = {
        'friend_diaries' : friendDiaryList
    }
    
    return render(request, 'diaries/community.html', context)


def communityTagSearchAjax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("query")  # 검색어
        
        if query:
            queries = list(set([item.strip() for item in query.split('#') if item]))

            # 현재 사용자의 이웃 목록 가져오기
            myNeighbors = Neighbor.objects.filter(Q(user1=request.user) | Q(user2=request.user))

            # 이웃들의 ID 가져오기 (현재 사용자를 제외한 친구들)
            neighbor_login_ids = set()
            for neighbor in myNeighbors:
                if neighbor.user1 != request.user:
                    neighbor_login_ids.add(neighbor.user1.login_id)
                if neighbor.user2 != request.user:
                    neighbor_login_ids.add(neighbor.user2.login_id)

            # 이웃들이 작성한 일기 가져오기
            friendAllDiaryList = Diary.objects.filter(writer__login_id__in=neighbor_login_ids)

            # 태그 필터링 적용
            if queries:
                friendAllDiaryList = friendAllDiaryList.filter(
                    tags__name__icontains=queries[0]
                )
                
                for q in queries[1:]:
                    friendAllDiaryList = friendAllDiaryList.filter(tags__name__icontains=q).distinct()

            # JSON 응답 반환
            result = [{
                "id": diary.id,
                "title": diary.title,
                "tags": list(diary.tags.values_list("name", flat=True)),
                "thumbnail": diary.four_cut_photo.image_file.url
                } for diary in friendAllDiaryList]
            return JsonResponse(result, safe=False)



def friend_request(request):
    return render(request, 'diaries/friend_request.html')

@login_required
def diary_map(request):
    myPlacesAddress = list(Diary.objects.filter(writer=request.user).values_list("place_address", flat=True))
    context = {
        "KAKAO_MAP_APPKEY_JS" : KAKAO_APPKEY_JS,
        "my_places_address" : myPlacesAddress,
    }
    return render(request, 'diaries/diary_map.html', context)

@login_required
def mydiaries(request):
    myDiaryList = Diary.objects.filter(writer=request.user)
    context = {
        'my_diaries' : myDiaryList
    }
    
    return render(request, 'diaries/mydiaries.html', context)

def mydiariesTagSearchAjax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("query")  # 검색어
        
        
        if query:
            queries = list(set([item.strip() for item in query.split('#') if item]))
            # 내 전체 일기 가져오기
            myAllDiaryList = Diary.objects.filter(writer=request.user)

            # 태그 필터링 적용
            if queries:
                myAllDiaryList = myAllDiaryList.filter(
                    tags__name__icontains=queries[0]
                )
                for q in queries[1:]:
                    myAllDiaryList = myAllDiaryList.filter(tags__name__icontains=q).distinct()

                # JSON 응답 반환
                result = [{
                    "id": diary.id,
                    "thumbnail": diary.four_cut_photo.image_file.url
                    } for diary in myAllDiaryList]
                return JsonResponse(result, safe=False)
        

@login_required
@transaction.atomic
def upload_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        uploaded_photo = request.FILES['photo']

        # 새로운 Frame 생성
        new_frame = Frame.objects.create(image_file=uploaded_photo)

        # 업로드한 사진을 Photo 모델에 저장
        Photo.objects.create(frame=new_frame, photo=uploaded_photo)

        # 저장 후 create_diary 페이지로 이동 (사진을 업로드한 Frame ID 포함)
        return redirect('diaries:create_diary', related_frame_id=new_frame.id)

    return redirect('diaries:select_photo_type')  # 실패하면 다시 선택 페이지로    

def diaries_by_place_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        place_address = data.get('address')
        
        diaries = Diary.objects.filter(writer=request.user, place_address=place_address).values('id','title', 'place')
        if not diaries.exists():
            return JsonResponse([], safe=False)  # 빈 리스트 반환
        diary_list = list(diaries)
        return JsonResponse(diary_list, safe=False)