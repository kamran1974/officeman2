# Generated by Django 4.2.10 on 2025-06-06 14:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0022_delete_messageread'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageSeen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seen_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان مشاهده')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seen_by_users', to='organization.message', verbose_name='پیام')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seen_messages', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'مشاهده پیام',
                'verbose_name_plural': 'مشاهده\u200cهای پیام',
                'unique_together': {('message', 'user')},
            },
        ),
    ]
