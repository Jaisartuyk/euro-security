# Generated manually for EURO SECURITY shift codes implementation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0008_medicalanalytics_and_more'),
    ]

    operations = [
        # Agregar campos para códigos de turno específicos
        migrations.AddField(
            model_name='shifttemplate',
            name='shift_code',
            field=models.CharField(
                max_length=5, 
                verbose_name='Código de Turno',
                help_text='Código específico del cliente (D, C, S, A, Y, etc.)',
                blank=True,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='shifttemplate',
            name='shift_category',
            field=models.CharField(
                max_length=20,
                verbose_name='Categoría de Turno',
                choices=[
                    ('GENERAL', 'General'),
                    ('CARGA_NACIONAL', 'Carga Nacional'),
                    ('CARGA_INTERNACIONAL', 'Carga Internacional'),
                ],
                default='GENERAL'
            ),
        ),
        migrations.AddField(
            model_name='shifttemplate',
            name='is_split_shift',
            field=models.BooleanField(
                verbose_name='Turno Dividido',
                default=False,
                help_text='Turno con descanso largo en el medio'
            ),
        ),
        migrations.AddField(
            model_name='shifttemplate',
            name='split_break_start',
            field=models.TimeField(
                verbose_name='Inicio Descanso Split',
                null=True,
                blank=True,
                help_text='Hora de inicio del descanso largo'
            ),
        ),
        migrations.AddField(
            model_name='shifttemplate',
            name='split_break_end',
            field=models.TimeField(
                verbose_name='Fin Descanso Split',
                null=True,
                blank=True,
                help_text='Hora de fin del descanso largo'
            ),
        ),
        migrations.AddField(
            model_name='shifttemplate',
            name='max_agents',
            field=models.PositiveIntegerField(
                verbose_name='Máximo Agentes',
                default=999,
                help_text='Máximo número de agentes para este turno'
            ),
        ),
        migrations.AddField(
            model_name='shifttemplate',
            name='weekday_schedule',
            field=models.JSONField(
                verbose_name='Horario por Día de Semana',
                default=dict,
                blank=True,
                help_text='Horarios específicos por día: {1: "05:45-17:45", 6: "05:30-17:30"}'
            ),
        ),
        migrations.AddField(
            model_name='shifttemplate',
            name='is_variable_schedule',
            field=models.BooleanField(
                verbose_name='Horario Variable',
                default=False,
                help_text='Turno con horario variable según itinerario (TAMPA)'
            ),
        ),
        
        # Agregar índice único para shift_code en PostgreSQL
        migrations.RunSQL(
            "CREATE UNIQUE INDEX attendance_shifttemplate_shift_code_unique ON attendance_shifttemplate (shift_code) WHERE shift_code IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS attendance_shifttemplate_shift_code_unique;"
        ),
    ]
