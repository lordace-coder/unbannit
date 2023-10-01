from django.conf import settings
from django.core.mail import send_mail


def send_gmail(title,message,reciever):
  send_mail(title,
            message,
          'freefireblackmarket@gmail.com',[reciever],
            fail_silently=False)

def send_unban_mail (email):
          send_gmail('unban account',"your unban request has been sent and will be confirmed within 12 days,any other use of hacks will result in a permanent ban",email)


def welcome_new_user(user):
  send_gmail(title="welcome user {}".format(user.username),
             message="Thank you for creating an account with us.",
             reciever=user.email)