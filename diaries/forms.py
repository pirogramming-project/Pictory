from django import forms
from .models import Diary
from users.models import User

class DiaryForm(forms.ModelForm):
    user_tags = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),  # 전체 유저 중에서 선택 가능  TODO: 추후 친구 목록으로 수정
        widget=forms.CheckboxSelectMultiple,  # 여러 개 선택할 수 있도록 체크박스 UI 제공
        required=False
    )
    
    class Meta:
        model = Diary
        fields = ["title", "date", "weather", "place", "emotion", "user_tags", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "name": "create_diary_title",
                    "placeholder": "제목을 작성해주세요",
                    "class": "create_diary_content_ksy",
                    "required": True,
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "name": "create_diary_day",
                    "placeholder": "날짜를 작성해주세요",
                    "class": "create_diary_content_ksy",
                    "type": "date",  # HTML5 캘린더 UI
                    "required": True,
                }
            ),
            "weather": forms.Select(
                attrs={
                    "class": "create_diaryButton_weather",
                    "name": "create_diary_weather",
                }
            ),
            "place": forms.TextInput(
                attrs={
                    "name": "create_diary_place",
                    "placeholder": "장소를 입력해주세요",
                    "class": "create_diary_content_ksy",
                    "required": True,
                }
            ),
            "emotion": forms.Select(
                attrs={
                    "class": "create_diaryButton_feeling",
                    "name": "create_diary_feeling",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "name": "create_diaryContent_ksy",
                    "placeholder": "일기를 작성해주세요",
                    "class": "create_diary_content_ksy",
                    "required": True,
                    "rows": 5,
                }
            ),
        }
