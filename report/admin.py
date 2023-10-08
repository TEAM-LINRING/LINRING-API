from django.contrib import admin
from django.contrib.admin import ModelAdmin
from report.models import Report


# Register your models here.
@admin.register(Report)
class ReportAdmin(ModelAdmin):
    base_model = Report
    list_display = [field.name for field in Report._meta.fields]
