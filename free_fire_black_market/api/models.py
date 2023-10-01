from core.mails import send_gmail
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
