from django.db import models
from django.contrib.auth.models import User
import uuid
import random

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="email_otp")
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  # 6-digit OTP
        self.save()
        return self.otp
