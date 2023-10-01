from django.conf import settings
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm, format_html


class CustomPaypalButton(PayPalPaymentsForm):
    def get_html_submit_element(self):
        return """<button type="submit" class="btn btn-primary">Purchase</button>"""
    
    def render_form(self,*args, **kwargs):
        form_open  = u'''<form action="%s" method="post">''' % (self.get_login_url())
        form_close = u'</form>'
        # format html as you need
        submit_elm = self.get_html_submit_element()
        return format_html(form_open+self.as_table()+submit_elm+form_close)


def generate_form_btn(amount,user,item_name,invoice,host)-> CustomPaypalButton:
        paypal_dict = {
            'business':settings.PAYPAL_RECIEVER_EMAIL,
            'amount':amount,
            'user':user,
            'item_name':item_name,
            'invoice':invoice,
            'currency_code':'USD',
            'notify_url':'http://{}{}'.format(host,reverse('paypal-ipn')),
            'cancel_url':'http://{}{}'.format(host,reverse('purchase_failed')),
            'return_url':'http://{}{}'.format(host,reverse('purchase_success',kwargs={'invoice_id':invoice})),
        }
        paypal_button =CustomPaypalButton(initial=paypal_dict)
        
        return paypal_button