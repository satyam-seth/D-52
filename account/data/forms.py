from django.utils.timezone import localtime,now,timedelta
from django import forms
from .models import Record,Water

class RecordFrom(forms.ModelForm):
    class Meta:
        model=Record
        fields=['date','name','item','price']
        widgets={
            'date':forms.DateInput(attrs={
                'type':'date',
                'class':'form-control',
                'min':localtime(now()-timedelta(6)).date(),
                'max':localtime(now()).date(),
                'value':localtime(now()).date()
                }),
            'item':forms.TextInput(attrs={'class':'form-control','placeholder':'Enter item name'}),
            'price':forms.NumberInput(attrs={'class':'form-control','min':'0','max':'5000','placeholder':'Enter item price'})
            }

class WaterFrom(forms.ModelForm):
    class Meta:
        model=Water
        fields=['date','quantity']
        widgets={'date':forms.DateInput(attrs={
            'type':'date',
            'class':'form-control',
            'min':localtime(now()-timedelta(20)).date(),
            'max':localtime(now()).date(),
            'value':localtime(now()).date()
            })}