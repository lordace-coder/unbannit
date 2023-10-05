from datetime import datetime, timedelta
from typing import Iterable, Optional

from api.token_generator import generate_token
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from helpers.format_date import format_time_ago, get_formatted_date

from .exceptions import UserSubscriptionError
from .mails import send_unban_mail


class Post(models.Model):
    title = models.CharField(max_length=250)
    post = models.TextField()
    slug = models.SlugField(default="empty")
    created_at = models.DateTimeField()
    image = models.ImageField(upload_to="posts/images")
    
    def __str__(self):
        return self.title
    
    def get_intro(self):
        return self.post[0:200]
    
    def save(self,*args, **kwargs) -> None:
        self.slug = slugify(self.title)
        self.created_at = datetime.now()
        return super().save(*args, **kwargs)
    
    @property
    def get_formatted_time(self):
        return format_time_ago(self.created_at)


# Create your models here.
class Comments(models.Model):
    author = models.CharField(max_length=100)
    comment = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(Post,related_name='comments',on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.author

    @property
    def get_formatted_time(self):
        return format_time_ago(self.created_at)



class Invoice(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    item_name = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    item_id = models.CharField(primary_key=True, max_length=8)
    paid = models.BooleanField(default = False)
    
    
    class Meta:
        db_table = 'invoice'
    
    def save(self, *args, **kwargs):

        self.item_id = Invoice.generate_uuid()

        super().save(*args, **kwargs)
    
    def format_date(self):
        return get_formatted_date(self.created_at)
    
    @staticmethod
    def generate_uuid():
        # Generate the primary key using the current date and time
        current_date = timezone.now().strftime("%m%d%y")
        last_generated_key = Invoice.objects.all().aggregate(models.Max('item_id'))['item_id__max']
        if last_generated_key and last_generated_key >= current_date:
            next_key = str(int(last_generated_key) + 1).zfill(6)
        else:
            next_key = current_date
            
        return next_key




class Store(models.Model):
    item_id = models.CharField(primary_key=True, max_length=6, editable=False)
    item_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency_code = models.CharField(max_length=3)
    amount_purchased = models.IntegerField(default=0)
    
    
    def __str__(self):
        return self.item_name
    
    
    
    
    @staticmethod
    def purchased(item_name):
        try:
            item = Store.objects.get(item_name = item_name)
            item.amount_purchased +=1
            item.save()
        except:
            pass
    
    
    @staticmethod
    def get_by_invoice(invoice:Invoice):
        try:
            qs = Store.objects.filter(item_name = invoice.item_name).first()
            if qs :
                return qs
        except:
            return
            
        
        
    def save(self, *args, **kwargs):
        if not self.item_id:
            # Generate the primary key using the current date and time
            current_date = timezone.now().strftime("%m%d%y")
            last_generated_key = Store.objects.all().aggregate(models.Max('item_id'))['item_id__max']
            if last_generated_key and last_generated_key >= current_date:
                next_key = str(int(last_generated_key) + 1).zfill(6)
            else:
                next_key = current_date
            self.item_id = next_key

        super().save(*args, **kwargs)


class FAQ(models.Model):
    question = models.CharField(max_length=150)
    reply = models.TextField(max_length=200)
    
    def __str__(self):
        return self.question
    
    class Meta:
        db_table = 'Faq'

    
class Subscription(models.Model):
    CHOICES = (
        ('A', 'gamer'),
        ('B', 'hacker'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null = True,blank = True)
    plan = models.CharField(max_length=1, choices=CHOICES)
    
    @property
    def active(self):
        return timezone.now().date() >= self.start_date and timezone.now().date() <= self.end_date

    # Add more fields as needed

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # Only update if the instance is not already saved
            if self.plan == 'A':
                self.end_date = timezone.now().date() + timedelta(days=30)
            elif self.plan == 'B':
                self.end_date = timezone.now().date() + timedelta(days=90)
                
        super().save(*args, **kwargs)
    
    def get_plan(self):
        plan = self.plan.lower()
        if plan == 'a':
            return 'gamer'
        else:
            return "hacker"


class MembershipToken(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    token = models.CharField(max_length=10)
    expiry_date = models.DateTimeField(null = True,blank = True)
    created_at = models.DateTimeField()
    
    
    def save(self, *args, **kwargs) -> None:
        if not self.created_at:
            self.created_at = timezone.now()
        if not self.expiry_date:
            self.expiry_date = self.created_at + timezone.timedelta(hours=24)
        return super().save(*args, **kwargs)
    
    @property
    def active(self):
        """
        verify if user's token is active
        """
        current_time = datetime.now()
        if self.expiry_date >= current_time:
            return False
        return True
        
    def __str__(self):
        return self.user.username
    
    @staticmethod
    def generate_token(user:User):
        """
            creates new token for user and delets previous existing tokens
        """
        user_subscription = Subscription.objects.get(user=user)
        if not user_subscription.active:
            raise UserSubscriptionError("user subscription is not active")
        
        qs = MembershipToken.objects.filter(user=user)
        if qs.exists():
            [item.delete() for item in qs]

        qs = MembershipToken.objects.create(user = user,token = generate_token(10))
        qs.save()
        return qs.token