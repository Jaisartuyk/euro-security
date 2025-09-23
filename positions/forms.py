from django import forms
from .models import Position
from departments.models import Department


class PositionForm(forms.ModelForm):
    """Formulario para crear y editar puestos de trabajo"""
    
    class Meta:
        model = Position
        fields = [
            'title', 'code', 'department', 'description', 'min_salary', 'max_salary',
            'level', 'employment_type', 'max_positions', 'is_active', 'is_hiring'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del puesto de trabajo'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único del puesto'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del puesto, responsabilidades y requisitos...'
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'max_positions': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_hiring': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar departamentos activos
        self.fields['department'].queryset = Department.objects.filter(is_active=True).order_by('name')
        self.fields['department'].empty_label = "Seleccionar departamento"
        
        # Hacer campos requeridos
        required_fields = ['title', 'code', 'department', 'min_salary', 'max_salary', 'level', 'employment_type']
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Verificar unicidad del código
            qs = Position.objects.filter(code=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un puesto con este código.")
        return code.upper() if code else code
    
    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        # Validar que el salario máximo sea mayor al mínimo
        if min_salary and max_salary:
            if max_salary <= min_salary:
                raise forms.ValidationError(
                    "El salario máximo debe ser mayor al salario mínimo."
                )
        
        return cleaned_data


class PositionFilterForm(forms.Form):
    """Formulario para filtrar puestos de trabajo"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título, código o descripción...'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label="Todos los departamentos",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    level = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los niveles')] + Position.POSITION_LEVELS,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    employment_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los tipos')] + Position.EMPLOYMENT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos'),
            ('active', 'Activos'),
            ('inactive', 'Inactivos')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    hiring = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos'),
            ('yes', 'En contratación'),
            ('no', 'Sin contratación')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
