from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from analysis.models import Profile
 

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.CharField(max_length=50, required=True)
    class Meta:
        model = User
        fields = ['username', 'email','first_name','last_name','password1','password2' ]
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name']
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # fields = ['user_image','phone_number','user_bio','cover_image']
        fields = ['profilepic','profession','bio','profilepic','phone','address','city','state','country','facebook','skype','linkedin','twitter']