from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field

class TextInputForm(forms.Form):
    text_input = forms.CharField(label= "", widget=forms.Textarea(attrs={'rows': 12, 'cols': 50, 'class': 'custom-field', 'placeholder': 'Enter the text you want to test for AI/Chatbot plagiarism (minimum 20 words).', 'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro;'} ))

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["Title", "Content"]

        widgets = {
            "Title": forms.TextInput(attrs={"class": "form-control", 'rows': 12, 'cols': 4, 'class': 'custom-field', 'placeholder': 'Enter your text...', 'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro;'}),
            "Content": forms.Textarea(attrs={"class": "form-control", 'rows': 12, 'cols': 50, 'class': 'custom-field', 'placeholder': 'Enter your text...', 'style': 'background-color: #FFF8DB; color: black; font-family: Source Code Pro;'}),
        }



