from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
from jalali_date_new.fields import JalaliDateTimeField, JalaliDateField
from jalali_date_new.widgets import AdminJalaliDateTimeWidget, AdminJalaliTimeWidget,\
									AdminJalaliDateWidget
from jalali_date_new.utils import datetime2jalali
from .models import VacationRequest, ProblemReport, Log
from django.utils.safestring import mark_safe
from django.urls import reverse


class LogInline(GenericTabularInline):
    model = Log
    verbose_name="لاگ"
    verbose_name_plural="لاگ ها"
    readonly_fields = ['user', 'action', 'created_jalali']

    @admin.display(description='زمان دقیق اقدام', ordering='created')
    def created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%Y-%m-%d - %H:%M')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    readonly_fields = ['created_jalali']
    list_display = (
        "user", "alternative", "start_jalali", "type", "duration", "status")
    list_filter = (
        "user", "alternative", "status")
    fieldsets = (
        (None, {"fields": ("user",)}),
        ("جزئیات درخواست", {"fields": (
            "alternative", "type", "duration", "description")}),
        ("تاریخ و زمان", {"fields": (
            "start_date", "end_date", "created_jalali",), }),
        ("وضعیت درخواست", {"fields": (
            "status",)}),

    )
    formfield_overrides = {
        models.DateTimeField:
            {
                'form_class': JalaliDateTimeField,
                "widget": AdminJalaliDateTimeWidget,
            },
    }
    inlines = [
        LogInline
    ]

    @admin.display(description='تاریخ ایجاد', ordering='created')
    def created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%Y-%m-%d - %H:%M')

    @admin.display(description='تاریخ شروع')
    def start_jalali(self, obj):
        return datetime2jalali(obj.start_date).strftime('%Y-%m-%d ساعت %H:%M')

    @admin.display(description='تاریخ پایان')
    def end_jalali(self, obj):
        return datetime2jalali(obj.end_date).strftime('%Y-%m-%d ساعت %H:%M')


@admin.register(ProblemReport)
class ProblemReportAdmin(admin.ModelAdmin):
    readonly_fields = ['created_jalali']
    list_display = (
        "type", "user", "description", "created_jalali", "effective")
    list_filter = (
        "user", "type", "effective")
    fieldsets = (
        ("اعلام کننده", {"fields": (
            "user",)}),
        ("جزئیات", {"fields": (
            "description", "corrective_actions", "prevention_actions",)}),
        ("وضعیت کنونی", {"fields": (
            "effective",)}),
        ("تاریخ و زمان", {"fields": (
            "created_jalali",), })
    )
    formfield_overrides = {
        models.DateTimeField:
            {
                'form_class': JalaliDateTimeField,
                "widget": AdminJalaliDateTimeWidget,
            },
    }

    @admin.display(description='تاریخ ایجاد', ordering='created')
    def created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%Y-%m-%d - %H:%M')


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'action', 'created',]
    list_display = ['user', 'action', 'created_jalali', 'log_content']
    fieldsets = (
        ("عامل", {"fields": (
            "user",)}),
        ("جزئیات", {"fields": (
            "action", "log_content")}),
        ("تاریخ و زمان", {"fields": (
            "created_jalali",), })
    )

    @admin.display(description='زمان دقیق اقدام', ordering='created')
    def created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%Y-%m-%d - %H:%M')

    @admin.display(description='هدف', ordering='created')
    #def log_content(self, obj):

    #    return mark_safe(f'<a href="{reverse('admin:%s_%s_change' % (obj.content_object._meta.app_label,  obj.content_object._meta.model_name), args=[obj.object_id])}">{obj.content_object}</a>')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
