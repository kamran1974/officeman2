from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


VACATION_TYPE = [
    ("ساعتی", "ساعتی"),
    ("روزانه", "روزانه")
]


VACATION_STATUS = [
    ("بررسی نشده", "بررسی نشده"),
    ("تایید جانشین", "تایید جانشین"),
    ("رد جانشین", "رد جانشین"),
    ("موافقت شده", "موافقت شده"),
    ("رد شده", "رد شده")
]


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="user_actions",
                             verbose_name="کاربر")
    action = models.TextField(max_length=250,
                            blank=True,
                            verbose_name="عمل انجام شده")
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return str(f"لاگ شماره: {self.pk}")

    class Meta:
        verbose_name = 'لاگ'
        verbose_name_plural = 'لاگ ها'
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class VacationRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="user_vacation_req",
                             verbose_name="نام متقاضی")
    alternative = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    related_name="alter_vacation_req",
                                    verbose_name="جایگزین")
    start_date = models.DateTimeField(blank=False,
                                      verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(blank=False,
                                    verbose_name="تاریخ پایان")
    duration = models.PositiveIntegerField(verbose_name="مدت")
    type = models.CharField(max_length=20,
                            choices=VACATION_TYPE,
                            verbose_name="نوع مرخصی")
    description = models.TextField(max_length=250,
                                   blank=True,
                                   verbose_name="توضیحات")
    status = models.CharField(max_length=20,
                              choices=VACATION_STATUS,
                              default="بررسی نشده",
                              verbose_name="وضعیت مرخصی")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'درخواست مرخصی'
        verbose_name_plural = 'درخواست های مرخصی'

    def __str__(self):
        return str(f'مرخصی {self.type} برای {self.user}')


class ProblemReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="user_problem_reports",
                             verbose_name="اعلام کننده")
    type = models.CharField(max_length=50,
                            blank=False,
                            verbose_name="نوع خطا")
    description = models.TextField(max_length=250,
                                   blank=True,
                                   verbose_name="توضیحات")
    corrective_actions = models.TextField(max_length=250,
                                          blank=True,
                                          verbose_name="اقدامات اصلاحی")
    prevention_actions = models.TextField(max_length=250,
                                          blank=True,
                                          verbose_name="اقدامات پیشگیری")
    effective = models.BooleanField(default=True,
                                    verbose_name="مؤثر بوده/نبوده")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ثبت خطا'
        verbose_name_plural = 'خطاهای ثبت شده'

    def __str__(self):
        return str(self.type)