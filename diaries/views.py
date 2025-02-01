from django.shortcuts import render, redirect
from .models import Diary, Frame, Tag
from django.contrib.auth.decorators import login_required
from .forms import DiaryForm
from datetime import date


# 인생네컷 추가 페이지3
def custom_photo(request):
    return render(request, 'diaries/custom_photo.html')


# 인생네컷 추가 페이지4
@login_required
def create_diary(request):
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