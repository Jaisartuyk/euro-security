from django import forms
from django.contrib.auth.models import User
from .models import Employee
from departments.models import Department
from positions.models import Position


class EmployeeForm(forms.ModelForm):
    """Formulario para crear y editar empleados"""
    
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'national_id',
            'date_of_birth', 'gender', 'marital_status', 'address', 'city', 'country',
            'department', 'position', 'hire_date', 'current_salary', 'is_active'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres del empleado'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos del empleado'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de identificación'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad de residencia'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'México'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'position': forms.Select(attrs={
                'class': 'form-select'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'current_salary': forms.NumberInput(attrs={
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
        
        # Filtrar departamentos y puestos activos
        self.fields['department'].queryset = Department.objects.filter(is_active=True).order_by('name')
        self.fields['position'].queryset = Position.objects.filter(is_active=True).order_by('title')
        
        # Configurar labels y help texts
        self.fields['department'].empty_label = "Seleccionar departamento"
        self.fields['position'].empty_label = "Seleccionar puesto"
        
        # Hacer campos requeridos
        required_fields = ['first_name', 'last_name', 'email', 'national_id', 'date_of_birth', 
                          'department', 'position', 'hire_date', 'current_salary']
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar unicidad del email
            qs = Employee.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un empleado con este correo electrónico.")
        return email
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if national_id:
            # Verificar unicidad del documento de identidad
            qs = Employee.objects.filter(national_id=national_id)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un empleado con este número de identificación.")
        return national_id
    
    def clean(self):
        cleaned_data = super().clean()
        hire_date = cleaned_data.get('hire_date')
        date_of_birth = cleaned_data.get('date_of_birth')
        
        # Validar que la fecha de nacimiento sea anterior a la fecha de contratación
        if hire_date and date_of_birth:
            from datetime import date
            age_at_hire = hire_date.year - date_of_birth.year
            if age_at_hire < 18:
                raise forms.ValidationError(
                    "El empleado debe tener al menos 18 años al momento de la contratación."
                )
        
        return cleaned_data


class EmployeeFilterForm(forms.Form):
    """Formulario para filtrar empleados"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, ID, email o documento...'
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
    
    position = forms.ModelChoiceField(
        queryset=Position.objects.filter(is_active=True).order_by('title'),
        required=False,
        empty_label="Todos los puestos",
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
