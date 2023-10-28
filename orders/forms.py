from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
  class Meta:
    model=Order
    fields= [ 'first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']
  def __init__(self, *args, **kwargs):
    super(OrderForm, self).__init__(*args, **kwargs)
    self.fields['first_name'].widget.attrs['placeholder']= 'Enter First Name'
    self.fields['last_name'].widget.attrs['placeholder']= 'Enter last name'
    self.fields['email'].widget.attrs['placeholder']= 'Email'
    self.fields['phone'].widget.attrs['placeholder']= 'Phone Number'
    self.fields['address_line_1'].widget.attrs['placeholder']= 'Address_line_1'
    self.fields['address_line_2'].widget.attrs['placeholder']= 'Address_line_2'
    self.fields['country'].widget.attrs['placeholder']= 'Country'
    self.fields['state'].widget.attrs['placeholder']= 'State'
    self.fields['city'].widget.attrs['placeholder']= 'City'
    self.fields['order_note'].widget = forms.Textarea(attrs={'placeholder': 'Order Note', 'class': 'form-control', 'rows': '2'})
    for field in self.fields:
      self.fields[field].widget.attrs['class']= 'form-control'
    