from django import forms
from django.forms import inlineformset_factory
from .models import UnitOutline, AssessmentItem


# Unit form + PDF upload validation
class UnitOutlineForm(forms.ModelForm):
    class Meta:
        model = UnitOutline
        fields = ['name', 'code', 'year_level', 'semester', 'status', 'release_as_vet', 'planner_pdf']
        widgets = {
            'planner_pdf': forms.ClearableFileInput(attrs={'accept': '.pdf'}),
        }

    def clean_planner_pdf(self):
        f = self.cleaned_data.get('planner_pdf')
        if f and hasattr(f, 'name') and not f.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Planner must be a PDF file.')
        return f



# Single assessment row
class AssessmentItemForm(forms.ModelForm):
    class Meta:
        model = AssessmentItem
        fields = ['name', 'weight', 'start_date', 'due_date']
        widgets = {
            'weight': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


# Inline formset linking assessments to a unit
AssessmentFormSet = inlineformset_factory(
    UnitOutline,
    AssessmentItem,
    form=AssessmentItemForm,
    extra=1,
    can_delete=True,
)
