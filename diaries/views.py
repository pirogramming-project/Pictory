from django.shortcuts import render, redirect
from .models import Diary, Frame, Sticker, Tag, Photo
from django.contrib.auth.decorators import login_required
from .forms import DiaryForm
from datetime import date


# 인생네컷 추가 페이지3
@login_required
def custom_photo(request):
    if request.method == "POST":
        '''사진 관련 데이터 몽땅 저장하고 다음 페이지로 이동 '''
        # 1. 사진 프레임 저장
        frame_css = request.POST.get("frame_css")  # 프레임 CSS 속성
        logo_text = request.POST.get("logo_text")  # 프레임 로고 속성

        if frame_css and logo_text:
            created_frame = Frame.objects.create(frame_css=frame_css, logo_text=logo_text)
            if not created_frame:
                print("[프레임]저장실패.. 다시시도")
                return render(request, 'diaries/custom_photo.html')
        
        # 2. 스티커 저장
        stickers_filenames = request.POST.getlist("sticker_srcs")  # 이미지 파일명들을 리스트로 받음
        stickers_Xs = request.POST.getlist("sticker_coorXs")
        stickers_Ys = request.POST.getlist("sticker_coorYs")
        if stickers_filenames:
            for i in range(len(stickers_filenames)):
                sticker_filename = stickers_filenames[i]
                sticker_X = stickers_Xs[i]
                sticker_Y = stickers_Ys[i]
                
                Sticker.objects.create(
                    frame=created_frame,
                    sticker_image=f'static/images/stickers/{sticker_filename}',
                    coor_x=sticker_X,
                    coor_y=sticker_Y
                    )
                
        # 3. 사진들 저장
        if request.FILES:
            uploaded_files = request.FILES.getlist("photos")  # 여러 개의 파일 받기
            print(uploaded_files)
            for file in uploaded_files:
                Photo.objects.create(frame=created_frame, photo=file)  # 이미지 저장
        
        # 저장 성공 시 리다이렉트
        if created_frame:
            return redirect("diaries:create_diary", created_frame.id)
        
        print("저장실패.. 다시시도?")
    
    return render(request, 'diaries/custom_photo.html')


# 인생네컷 추가 페이지4
@login_required
def create_diary(request, related_frame_id):
    related_frame = Frame.objects.get(id=related_frame_id)
    if request.method == 'POST':
        four_cut_photo = Frame.objects.create(frame_css = "test")   ## TODO: 실제 네컷사진 불러오는 걸로 수정 필요
        
        form = DiaryForm(request.POST)
        if form.is_valid():
            diary = form.save(commit=False) # 유저태그 빼고 저장
            if not diary.date:
                diary.date = date.today()  # 일기 날짜가 입력되지 않았으면 오늘 날짜로 설정
                
            # diary의 다른 필드들 추가하고 diary 먼저 저장.
            diary.writer = request.user
            diary.four_cut_photo = four_cut_photo
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
            

            return redirect('/')    # 페이지 리다이렉션 디테일페이지 미구현
        else:
            print("error: form is not valid")
            return redirect('diaries:create_diary')
        
    form = DiaryForm()
    context = {
        'form' : form,
    }
    return render(request, 'diaries/create_diary.html', context)