from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ArtistProfile, Artwork

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(max_length=80)
    class Meta:
        model = User
        fields = ("username","email","display_name","password1","password2")

class ProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = ("display_name","bio","avatar","country","website")
        widgets = {"bio": forms.Textarea(attrs={"rows":4})}

class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ("title","description","image","medium","ai_declared")
        widgets = {"description": forms.Textarea(attrs={"rows":4})}
