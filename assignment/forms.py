from django import forms 
from .models import Assignment
class CustomAssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'assignment_title',
            'assignment_description',
            'learning_objectives',
            'has_ai_component',
            'is_collaborative',
            'assignment_type',
            'subject',
            'percent_of_cheating_students',
        ]
        widgets = {
            'assignment_title': forms.TextInput(attrs={'class': 'custom-form-field'}),
            'assignment_description': forms.Textarea(attrs={'class': 'custom-form-field', 'rows': 4}),
            'learning_objectives': forms.TextInput(attrs={'class': 'custom-form-field'}),
            'has_ai_component': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
            'is_collaborative': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
            'assignment_type': forms.Select(attrs={'class': 'custom-form-field'}),
            'subject': forms.Select(attrs={'class': 'custom-form-field'}),
            'percent_of_cheating_students': forms.NumberInput(attrs={'class': 'custom-form-field'}),
        }