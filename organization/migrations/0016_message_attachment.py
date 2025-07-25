# Generated by Django 4.2.10 on 2025-06-02 15:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0015_remove_taskassignment_remind_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255, verbose_name='موضوع')),
                ('body', models.TextField(blank=True, verbose_name='متن')),
                ('scheduled_time', models.DateTimeField(blank=True, null=True, verbose_name='زمانبندی ارسال')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')),
                ('sent', models.BooleanField(default=False, verbose_name='وضعیت ارسال')),
                ('recipients', models.ManyToManyField(related_name='received_messages', to=settings.AUTH_USER_MODEL, verbose_name='گیرندگان')),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='organization.message', verbose_name='پاسخ به')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL, verbose_name='فرستنده')),
            ],
            options={
                'verbose_name': 'پیام',
                'verbose_name_plural': 'پیام ها',
                'permissions': [('privileged_view_messages', 'می تواند تمام پیام های کاربران را ببیند')],
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, upload_to='message_attachments/', verbose_name='فایل')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان آپلود')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='organization.message', verbose_name='پیام مربوطه')),
            ],
            options={
                'verbose_name': 'ضمیمه پیام',
                'verbose_name_plural': 'ضمیمه های پیام',
            },
        ),
    ]
