from django import forms
from .models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["nickname", "email", "birthday", "name", "introduce"] 
        widgets = {
            "nickname": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "birthday": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),  
            "introduce": forms.Textarea(attrs={"class": "form-control", "rows": 3}),  
        }
