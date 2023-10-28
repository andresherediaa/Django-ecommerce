from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
  confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Confirm password',
    'class': 'form-control'
  }))
  password=forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Enter password',
    'class': 'form-control'
  }))
  
  class Meta:
    model=Account
    fields= ['first_name', 'last_name', 'email', 'phone_number','password']
  
  def __init__(self, *args, **kwargs):
    super(RegistrationForm, self).__init__(*args, **kwargs)
    self.fields['first_name'].widget.attrs['placeholder']= 'Enter First Name'
    self.fields['last_name'].widget.attrs['placeholder']= 'Enter last name'
    self.fields['email'].widget.attrs['placeholder']= 'Enter Email'
    self.fields['phone_number'].widget.attrs['placeholder']= 'Enter Phone Number'
    for field in self.fields:
      self.fields[field].widget.attrs['class']= 'form-control'
      
  def clean_confirm_password(self): ##clean make it execute automaticallly after post
    password = self.cleaned_data.get('password')
    confirm_password =self.cleaned_data.get('confirm_password')
    if password != confirm_password:
      raise forms.ValidationError("!Error: Passwords are different")
    return confirm_password
  
class RestorePasswordForm(forms.ModelForm):
  confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Confirm password',
    'class': 'form-control'
  }))
  password=forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Enter password',
    'class': 'form-control'
  }))
  
  class Meta:
    model=Account
    fields= ['password']
 
  def clean_confirm_password(self): ##clean make it execute automaticallly after post
    password = self.cleaned_data.get('password')
    confirm_password =self.cleaned_data.get('confirm_password')
    if password != confirm_password:
      raise forms.ValidationError("!Error: Passwords are different")
    return confirm_password
      
    
    
    