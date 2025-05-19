from django.db import models
from django.contrib.auth.models import User

class OtpCode(models.Model):
    username_phone = models.ForeignKey(User,on_delete=models.CASCADE)
    code = models.CharField(max_length=6,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.username_phone} - {self.code}"