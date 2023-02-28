from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# class TextInputForm(forms.Form):
#     text_input = forms.CharField(label= "", widget=forms.Textarea(attrs={'rows': 12, 'cols': 50, 'class': 'custom-field', 'placeholder': 'Enter the text you want to test for AI/Chatbot plagiarism (minimum 20 words).', 'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro;'} ))

from .models import Feedback

class TextInputForm(forms.Form):
    text_input = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 10, 'cols': 35, 'class': 'custom-field border-black', 'placeholder': 'Enter the text you want to test for AI/Chatbot plagiarism (minimum 20 words)', 'style': 'background-color: #FFF8DB; color: rgb(0,0,0); font-family: Source Code Pro; font-size: 13px; border-color: black;'} ))
    file_input = forms.FileField(required=False, widget=forms.ClearableFileInput(
            attrs={
                'class': 'custom-file-input',
                'id': 'customFile',
                'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro; font-size: 13px;',
                'multiple': True,
            } ))

    def clean(self):
        cleaned_data = super().clean()
        text_input = cleaned_data.get('text_input')
        file_input = cleaned_data.get('file_input')
        if not text_input and not file_input:
            raise forms.ValidationError('Either a text input or a file input is required')
        elif text_input and file_input:
            raise forms.ValidationError('Only one of text input or file input can be submitted')
        if text_input: 
            word_count = len(text_input.split())
            if word_count < 20:
                raise ValidationError(_('The text input must be at least 20 words.'), code='invalid')
        return cleaned_data

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['Name','Email',"Title", "Content"]

        # widgets = {
        #     "Name": forms.TextInput(attrs={"class": "form-control", 'rows': 12, 'cols': 4, 'class': 'custom-field', 'placeholder': 'Enter your text...', 'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro;'}),
        #     "Email": forms.TextInput(attrs={"class": "form-control", 'rows': 12, 'cols': 4, 'class': 'custom-field', 'placeholder': 'Enter your text...', 'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro;'}),
        #     "Title": forms.TextInput(attrs={"class": "form-control", 'rows': 12, 'cols': 4, 'class': 'custom-field', 'placeholder': 'Enter your text...', 'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro;'}),
        #     "Content": forms.Textarea(attrs={"class": "form-control", 'rows': 12, 'cols': 50, 'class': 'custom-field', 'placeholder': 'Enter your text...', 'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro;'}),
        # }
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Email': forms.TextInput(attrs={'class': 'form-control'}),
            'Title': forms.TextInput(attrs={'class': 'form-control'}),
            'Content': forms.Textarea(attrs={'class': 'form-control','rows': 2, 'cols': 4,}),
         }
