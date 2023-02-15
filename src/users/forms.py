from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import User

#class UserRegisterForm(UserCreationForm):
 #   email = forms.EmailField()

  #  class Meta:
   #     model = Patient
    #    fields = ['username', 'email', 'password']

# Create a UserUpdateForm to update a username and email
#class UserUpdateForm(forms.ModelForm):
 #   email = forms.EmailField()

    #class Meta:
   #     model = Patient
  #      fields = ['username', 'email']

# Create a ProfileUpdateForm to update image.
#class ProfileUpdateForm(forms.ModelForm):
 #  class Meta:
  ##    fields = ['image']