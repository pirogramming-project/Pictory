from django.shortcuts import render, redirect, get_object_or_404
from .models import Diary, Frame, Tag, User_Tag, User
from django.contrib.auth.decorators import login_required
from .forms import DiaryForm
from datetime import date
from django.urls import reverse


# 디테일 페이지
def diary_detail(request, diary_id):
    diary = get_object_or_404(Diary, id=diary_id)  
    user_tags = User_Tag.objects.filter(diary=diary)  
    return render(request, 'diaries/detail.html', {'diary': diary, 'user_tags': user_tags})

@login_required
def edit_diary(request, diary_id):
    diary = get_object_or_404(Diary, id=diary_id)

    if request.method == 'POST':
        form = DiaryForm(request.POST, instance=diary)

        if form.is_valid():
            print("폼 검증 성공")
            diary = form.save(commit=False)
            diary.save()
            form.save_m2m()

            # 기존 태그 삭제 후 새 태그 저장
            diary.tags.clear()  
            tag_string = request.POST.get('create_diary_post', '')
            tag_list = [tag.strip() for tag in tag_string.split('#') if tag.strip()]
            for tag in tag_list:
                new_tag, created = Tag.objects.get_or_create(diary=diary, name=tag)

            # 기존 유저 태그 삭제 후 새 태그 저장
            User_Tag.objects.filter(diary=diary).delete()
            user_ids = request.POST.getlist('user_tags')
            selected_users = User.objects.filter(id__in=user_ids)  

            for user in selected_users:
                User_Tag.objects.create(diary=diary, user=user)

            return redirect(reverse('diaries:diary_detail', kwargs={'diary_id': diary.id}))


        else:
            print("폼 유효성 검사 실패:", form.errors)  # 에러 확인용

    else:
        form = DiaryForm(instance=diary)

    all_users = User.objects.all()
    user_tags = diary.user_tags.all()
    diary_tags = diary.tags.all()

    context = {
        'form': form,
        'diary': diary,
        'all_users': all_users,
        'user_tags': user_tags,
        'diary_tags': diary_tags,
    }
    return render(request, 'diaries/edit_diary.html', context)


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