<<<<<<< HEAD
from django.db import models
from django.conf import settings
from .managers import UserManager
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    username, date_joined = None, None
    id_number = models.CharField(max_length=10,
                                 unique=True,
                                 verbose_name="کد ملی")
    phone_number = models.CharField(max_length=11,
                                    unique=True,
                                    verbose_name="تلفن همراه")
    USERNAME_FIELD = "id_number"
    REQUIRED_FIELDS = ["phone_number"]

    objects = UserManager()

    def __str__(self):
=======
from django.db import models
from django.conf import settings
from .managers import UserManager
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    username, date_joined = None, None
    id_number = models.CharField(max_length=10,
                                 unique=True,
                                 verbose_name="کد ملی")
    phone_number = models.CharField(max_length=11,
                                    unique=True,
                                    verbose_name="تلفن همراه")
    USERNAME_FIELD = "id_number"
    REQUIRED_FIELDS = ["phone_number"]

    objects = UserManager()

    def __str__(self):
>>>>>>> 3d29c33 (New feature TODOLIST added)
        return str(f'{self.first_name} {self.last_name}')