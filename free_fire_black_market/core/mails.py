from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_gmail(title,message,reciever):
  html_message = render_to_string('mails/forgot_password/index.html',{'message':message})
  plain_msg = strip_tags(html_message)
  message = EmailMultiAlternatives(
    subject=title,
    body=plain_msg,
    from_email='freefireblackmarket@gmail.com',
    to=[reciever]
  )
  message.attach_alternative(html_message,'text/html')
  message.send(fail_silently=True)




def send_unban_mail (email):
  html_message = render_to_string('mails/confirm_unban/index.html')
  plain_msg = strip_tags(html_message)
  message = EmailMultiAlternatives(
    subject='Unban Confirmation',
    body=plain_msg,
    from_email='freefireblackmarket@gmail.com',
    to=[email]
  )
  message.attach_alternative(html_message,'text/html')
  message.send(fail_silently=True)


def welcome_new_user(user):
  html_message = render_to_string('mails/welcome/index.html')
  plain_msg = strip_tags(html_message)
  message = EmailMultiAlternatives(
    subject=f'Welcome {user.username}',
    body=plain_msg,
    from_email='freefireblackmarket@gmail.com',
    to=[user.email]
  )
  message.attach_alternative(html_message,'text/html')
  message.send(fail_silently=True)
