from django import forms
from django.contrib.auth.models import User
from .models import Department, DepartmentBudget


class DepartmentForm(forms.ModelForm):
    """Formulario para crear y editar departamentos"""
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'department_type', 'description', 'manager', 'budget', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del departamento'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único (ej: RRHH, SIS)',
                'maxlength': '10'
            }),
            'department_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción del departamento'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios que pueden ser jefes de departamento
        self.fields['manager'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['manager'].empty_label = "Seleccionar jefe de departamento"
        
        # Hacer que el código sea único
        if self.instance.pk:
            self.fields['code'].help_text = "El código debe ser único en el sistema"
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper()
            # Verificar unicidad
            qs = Department.objects.filter(code=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un departamento con este código.")
        return code


class DepartmentBudgetForm(forms.ModelForm):
    """Formulario para presupuestos departamentales"""
    
    class Meta:
        model = DepartmentBudget
        fields = ['year', 'month', 'allocated_budget', 'spent_budget', 'notes']
        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2030'
            }),
            'month': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
                (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
                (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
            ]),
            'allocated_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'spent_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales sobre el presupuesto'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        allocated_budget = cleaned_data.get('allocated_budget')
        spent_budget = cleaned_data.get('spent_budget')
        
        if allocated_budget and spent_budget:
            if spent_budget > allocated_budget:
                raise forms.ValidationError(
                    "El presupuesto gastado no puede ser mayor al presupuesto asignado."
                )
        
        return cleaned_data


class DepartmentFilterForm(forms.Form):
    """Formulario para filtrar departamentos"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, código o descripción...'
        })
    )
    
    department_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los tipos')] + Department.DEPARTMENT_TYPES,
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
