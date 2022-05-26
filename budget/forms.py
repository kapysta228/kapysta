from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User

from unidecode import unidecode

from .models import Operation, Category, Family


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name']


class OperationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['value', 'description', 'category']:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': self.fields[field].label})
        self.fields['value'].widget.attrs.update({'min': 0})
        self.fields['description'].widget.attrs.update({'list': 'desc-list'})

    class Meta:
        model = Operation
        fields = ['value', 'description', 'category']

    def clean_value(self):
        value = self.cleaned_data['value']
        if value < 0 or value == 0:
            raise ValidationError("Введено некорректное значение")
        return value


class CategoryForm(forms.ModelForm):
    user_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['name', 'type_pay']:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': self.fields[field].label})

    class Meta:
        model = Category
        fields = ['name', 'type_pay', 'user_id']

    def clean(self):
        user_id = self.cleaned_data['user_id']
        name = self.cleaned_data['name']
        type_pay = self.cleaned_data['type_pay']

        if Category.objects.filter(user_id=user_id, name=name, type_pay=type_pay).exists():
            raise ValidationError({'name': 'Категория уже существует'})
        return self.cleaned_data
