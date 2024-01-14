from django import forms 
from .models import Assignment
from django.core.exceptions import ValidationError
class CustomAssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'assignment_title',
            'assignment_description',
            'assignment_criteria',
            'total_marks',           
            'subject',
            
        ]
        widgets = {
            'assignment_title': forms.TextInput(attrs={'class': 'custom-form-field rounded', 'placeholder': "Add Your Assignment's Title", 'label': "",}),
            'assignment_description': forms.Textarea(attrs={'class': 'custom-form-field rounded', 'rows': 4, 'placeholder': "Add Your Student's Directives/Instructions"}),        
            'assignment_criteria': forms.TextInput(attrs={'class': 'custom-form-field rounded', 'placeholder': "Add Your Assignment's Criteria"}),
            'total_marks': forms.NumberInput(attrs={'class': 'custom-form-field rounded', 'placeholder': "Add Assignment's Total Marks"}),        
            'subject': forms.Select(attrs={'class': 'custom-form-field rounded'}),
            
        }
        def clean(self):
            cleaned_data = super().clean()
            percent = cleaned_data.get('percent_of_cheating_students')
            if percent: 
                if percent < 0:
                    raise ValidationError(('The cheating percentage must be greater than or equal to 0.'), code='invalid')
                elif percent > 100:
                    raise ValidationError(('The cheating percentage must be less than or equal to 100.'), code='invalid')
            return cleaned_data