# -*- coding: utf-8 -*-
from django import forms
from apps.orders.models import Order, OneClickBye

class RegistrationOrderForm(forms.ModelForm):
    first_name = forms.CharField(error_messages={'required': 'Введите ваше имя'})
    last_name = forms.CharField(error_messages={'required': 'Введите вашу фамилию'})
    email = forms.EmailField(error_messages={'required': 'Введите ваш e-mail'})
    phone = forms.CharField(error_messages={'required': 'Введите ваш номер телефона'})
    note = forms.CharField(
        widget=forms.Textarea(),
        required=False
    )

    class Meta:
        model = Order
        exclude = ('create_date',)

    def clean(self):
        cleaned_data = super(RegistrationOrderForm, self).clean()
        order_carting = cleaned_data.get("order_carting")
        address = cleaned_data.get("address")

        if order_carting == 'carting' and address=='':
            raise forms.ValidationError("Введите адрес доставки")

        return cleaned_data

class OneClickByeForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.TextInput(),required=True)

    class Meta:
        model = OneClickBye
        exclude = ('create_date',)