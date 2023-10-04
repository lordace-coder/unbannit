from collections.abc import Iterable
from datetime import datetime, timedelta, timezone

from core.mails import send_gmail
from django.contrib.auth.models import User
from django.db import models

from .token_generator import generate_token


# Create your models here.
class Token(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=10)
    
    def __str__(self):
        return self.email
    
    @staticmethod
    def verify_token(email,token)->bool:
        qs = Token.objects.filter(email=email,token=token)
        if qs.exists():
            for item in qs:
                item.delete()
            return True
        return False

  
    @staticmethod
    def generate_token(email):
        try:
            new_token  = generate_token(6)
            qs = Token.objects.create(email=email,token=new_token)
            qs.save()
            # mail token to email address
            send_gmail(
                title='Account Recovery Token',
                message= f'Your recovery token is {new_token} dont share it with anyone',
                reciever=email
            )
            
        except Exception as e:
            return e

class UnbanActive(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True)
    unban_time = models.DateTimeField(null = True,blank = True)
    
    def __str__(self):
        return self.user.username
    
    def save(self,*args, **kwargs) -> None:
        
        if not self.unban_time:
            self.unban_time = self.created_at + timedelta(days = 12)
        return super().save(*args, **kwargs)
    
    @property
    def is_unbanned(self)->bool:
        
        return (datetime.now(tz=timezone.utc) >= self.unban_time.replace(tzinfo=timezone.utc))
    
   
    def time_left(self)->timedelta:
        if self.is_unbanned:return
        unban_time = self.unban_time.replace(tzinfo=timezone.utc)
        result =  (datetime.now(timezone.utc)-unban_time)
        
        return abs(result.total_seconds())
    
    
