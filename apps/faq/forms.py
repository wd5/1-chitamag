# -*- coding: utf-8 -*-
from django import forms
from apps.faq.models import Question

class QuestionForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'required':'required',
            }
        ),
        required=True
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'required':'required',
            }
        ),
        required=True
    )
    question = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'required':'required',
            }
        ),
        required=True
    )

    class Meta:
        model = Question
        fields = ('name', 'email', 'question',)