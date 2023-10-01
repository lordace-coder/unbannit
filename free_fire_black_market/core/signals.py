from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from .mails import welcome_new_user
from .models import Invoice, Store, Subscription, User


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender

    if ipn_obj.payment_status == ST_PP_COMPLETED:

        if ipn_obj.receiver_email != settings.PAYPAL_RECIEVER_EMAIL:
            # Not a valid payment
            return

        try:
            my_pk = ipn_obj.invoice
            mytransaction = Invoice.objects.get(item_id = my_pk)
            mytransaction.paid = True
            mytransaction.save()
            
            # mark item as purchased
            Store.purchased(ipn_obj.item_name)
        except Exception as e:
   
            ...
        else:
            mytransaction.paid = True
            mytransaction.save()
            if 'plan' in mytransaction.item_name:
                print('chckpoint')
                item = Store.objects.get(item_name = ipn_obj.item_name)
                subscription_plan = 'A' if 'gamer' in mytransaction.item_name else 'B'
                # check if subscribtion already exists
                active_sub = Subscription.objects.filter(user = mytransaction.user)
                if active_sub.exists():
                    for i in active_sub:
                        i.delete()
                
                
                new_sub = Subscription.objects.create(plan = subscription_plan,user = mytransaction.user)
                new_sub.save()
                
    else:
        print('Paypal payment status not completed: %s' % ipn_obj.payment_status)



"""
    send welcome message (mail) to a new user once they create an account for the first time
"""
@receiver(post_save,sender=User)
def send_welcome_mail(sender,instance,created,*args, **kwargs):
    if created:
        welcome_new_user(instance)