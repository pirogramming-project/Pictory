from django import forms
from .models import Diary
from users.models import User
from django.utils.safestring import mark_safe
from django.forms.widgets import RadioSelect

# 감정 점수와 SVG 매핑
EMOTION_CHOICES = [
    (1, '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-angry" viewBox="0 0 16 16">'
        '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>'
        '<path d="M4.285 12.433a.5.5 0 0 0 .683-.183A3.5 3.5 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.5 4.5 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683m6.991-8.38a.5.5 0 1 1 .448.894l-1.009.504c.176.27.285.64.285 1.049 0 .828-.448 1.5-1 1.5s-1-.672-1-1.5c0-.247.04-.48.11-.686a.502.502 0 0 1 .166-.761zm-6.552 0a.5.5 0 0 0-.448.894l1.009.504A1.94 1.94 0 0 0 5 6.5C5 7.328 5.448 8 6 8s1-.672 1-1.5c0-.247-.04-.48-.11-.686a.502.502 0 0 0-.166-.761z"/>'
        '</svg>'),
    (2, '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-frown" viewBox="0 0 16 16">'
        '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>'
        '<path d="M4.285 12.433a.5.5 0 0 0 .683-.183A3.5 3.5 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.5 4.5 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683M7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5m4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5"/>'
        '</svg>'),
    (3, '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-neutral" viewBox="0 0 16 16">'
        '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>'
        '<path d="M4 10.5a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 0-1h-7a.5.5 0 0 0-.5.5m3-4C7 5.672 6.552 5 6 5s-1 .672-1 1.5S5.448 8 6 8s1-.672 1-1.5m4 0c0-.828-.448-1.5-1-1.5s-1 .672-1 1.5S9.448 8 10 8s1-.672 1-1.5"/>'
        '</svg>'),
    (4, '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-smile" viewBox="0 0 16 16">'
        '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>'
        '<path d="M4.285 9.567a.5.5 0 0 1 .683.183A3.5 3.5 0 0 0 8 11.5a3.5 3.5 0 0 0 3.032-1.75.5.5 0 1 1 .866.5A4.5 4.5 0 0 1 8 12.5a4.5 4.5 0 0 1-3.898-2.25.5.5 0 0 1 .183-.683M7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5m4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5"/>'
        '</svg>'),
    (5, '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-neutral" viewBox="0 0 16 16">'
        '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>'
        '<path d="M4 10.5a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 0-1h-7a.5.5 0 0 0-.5.5m3-4C7 5.672 6.552 5 6 5s-1 .672-1 1.5S5.448 8 6 8s1-.672 1-1.5m4 0c0-.828-.448-1.5-1-1.5s-1 .672-1 1.5S9.448 8 10 8s1-.672 1-1.5"/>'
        '</svg>'),
    (6, '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-grin" viewBox="0 0 16 16">'
        '<path d="M12.946 11.398A6.002 6.002 0 0 1 2.108 9.14c-.114-.595.426-1.068 1.028-.997C4.405 8.289 6.48 8.5 8 8.5s3.595-.21 4.864-.358c.602-.07 1.142.402 1.028.998a5.95 5.95 0 0 1-.946 2.258m-.078-2.25C11.588 9.295 9.539 9.5 8 9.5s-3.589-.205-4.868-.352c.11.468.286.91.517 1.317A37 37 0 0 0 8 10.75a37 37 0 0 0 4.351-.285c.231-.407.407-.85.517-1.317m-1.36 2.416c-1.02.1-2.255.186-3.508.186s-2.488-.086-3.507-.186A5 5 0 0 0 8 13a5 5 0 0 0 3.507-1.436ZM6.488 7c.114-.294.179-.636.179-1 0-1.105-.597-2-1.334-2C4.597 4 4 4.895 4 6c0 .364.065.706.178 1 .23-.598.662-1 1.155-1 .494 0 .925.402 1.155 1M12 6c0 .364-.065.706-.178 1-.23-.598-.662-1-1.155-1-.494 0-.925.402-1.155 1a2.8 2.8 0 0 1-.179-1c0-1.105.597-2 1.334-2C11.403 4 12 4.895 12 6"/>'
        '<path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m0-1A7 7 0 1 1 8 1a7 7 0 0 1 0 14"/>'
        '</svg>'),
    (7, '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-emoji-heart-eyes" viewBox="0 0 16 16">'
        '<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>'
        '<path d="M11.315 10.014a.5.5 0 0 1 .548.736A4.5 4.5 0 0 1 7.965 13a4.5 4.5 0 0 1-3.898-2.25.5.5 0 0 1 .548-.736h.005l.017.005.067.015.252.055c.215.046.515.108.857.169.693.124 1.522.242 2.152.242s1.46-.118 2.152-.242a27 27 0 0 0 1.109-.224l.067-.015.017-.004.005-.002zM4.756 4.566c.763-1.424 4.02-.12.952 3.434-4.496-1.596-2.35-4.298-.952-3.434m6.488 0c1.398-.864 3.544 1.838-.952 3.434-3.067-3.554.19-4.858.952-3.434"/>'
        '</svg>'),
]

class SVGRadioRenderer(RadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        for choice_value, choice_label in self.choices:
            is_checked = 'checked' if str(value) == str(choice_value) else ''  # 기존 선택값과 비교
            svg = mark_safe(choice_label)  # SVG를 HTML로 안전하게 렌더링
            input_html = f'<input type="radio" name="{name}" value="{choice_value}" id="{name}_{choice_value}" {is_checked} />'
            label_html = f'<label for="{name}_{choice_value}">{svg}</label>'
            output.append(f'<div class="emotion-choice">{input_html} {label_html}</div>')
        return mark_safe('\n'.join(output))

class DiaryForm(forms.ModelForm):
    user_tags = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),         # 전체 유저 중에서 선택 가능  TODO: 추후 친구 목록으로 수정
        widget=forms.CheckboxSelectMultiple,  # 여러 개 선택할 수 있도록 체크박스 UI 제공
        required=False
    )
    emotion = forms.ChoiceField(
        choices=EMOTION_CHOICES,
        widget=SVGRadioRenderer
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
            # "emotion": forms.Select(
            #     attrs={
            #         "class": "create_diaryButton_feeling",
            #         "name": "create_diary_feeling",
            #     }
            #),
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
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user_tags"].queryset = User.objects.all()  # 실제 user 목록 설정 # TODO: 추후 전체 유저 말고 친구 목록에서 가져오도록 수정.
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['emotion'].initial = kwargs['instance'].emotion
