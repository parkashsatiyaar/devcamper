from django.db import models
from django.http import request
from django.contrib.auth.models import User
# Create your models here.


class Role(models.Model):
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.role


class tblUser(models.Model):
    userid = models.OneToOneField(
        User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    isactive = models.BooleanField(default=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to="profile/%Y/%m/%d/", null=True)
    isdeleted = models.BooleanField(default=False)

    def __str__(self):
        return self.username
