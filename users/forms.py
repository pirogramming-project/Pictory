from django import forms
from .models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["nickname", "email", "birthday", "name", "introduce"] 
        widgets = {
            "nickname": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "birthday": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "name": forms.TextInput(attrs={"class": "form-control"}),  
            "introduce": forms.TextInput(attrs={"class": "form-control"}),  
        }
    nickname = forms.CharField(
        required=True,  
        widget=forms.TextInput(attrs={"class": "form-control"})  #수정 가능하게 변경
    )
    name = forms.CharField(required=False)
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d")
    )
    introduce = forms.CharField(required=False)
    email = forms.CharField(required=False)

    def clean_birthday(self):
        birthday = self.cleaned_data.get("birthday")
        return birthday if birthday else None  

