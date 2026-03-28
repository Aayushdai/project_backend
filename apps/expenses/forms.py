from django import forms
from .models import Expense
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description','amount', 'paid_by','split_among']
        widgets = {
            'description' :forms.TextInput(attrs={'placeholder' : 'e.g Lunch in Pokhara'}),
            'amount' : forms.NumberInput(attrs={'step':'0.01' ,'min':'0'}),
            'paid_by' : forms.Select(attrs={'class' : 'form_select'}),
            'split_among' : forms.SelectMultiple(attrs={'class': 'form_select'})
        }

        def __init__(self ,*args, **kwargs):
            super().__init__(*args, **kwargs)