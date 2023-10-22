from typing import Any, Dict

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import models
from django.db.models.query import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.base import TemplateResponseMixin
from helpers.math import get_discount, reduce_by

from .forms import CustomPaypalButton, generate_form_btn
from .mails import send_unban_mail
from .models import FAQ, Invoice, Post, Store, Subscription

# from django.

def not_found(request,exception):
    return render(request,'404.html',status=404)


class HomeView(ListView):
    template_name = "index.html"
    queryset = Post.objects.all()
    context_object_name = "post"
    
    def get_queryset(self) -> QuerySet[Any]:
        qs =  super().get_queryset()[0:3]
        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context= super().get_context_data(**kwargs)
        context['faq'] = FAQ.objects.all()
        
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
            
        return context


  
class UnbanAcctView(TemplateView):
    template_name = 'unbann.html'



class ContactPageView(TemplateView):
    template_name = 'contact_us.html'
    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        context = dict()
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
        if kwargs.get('status') == 'report':
            context = {'subject':'Customer Report'}

            return render(request,self.template_name,context)
        elif kwargs.get('status'):
            raise http.Http404
        return render(request,self.template_name,context)
        




class TutorialPageView(TemplateView):
    template_name = "tutorial_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_tab = self.kwargs.get('selected_tab')
        if selected_tab:
            context['current_tab'] = selected_tab
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
        return context
    


class HandleUnbanView(LoginRequiredMixin,TemplateView):
    template_name = 'handle_unban.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        host = self.request.get_host()
        item:Store = Store.objects.get(item_id = '082425')
        
        # get amount to check for discount
        amount = item.amount
        # generate unique key
        invoice_number = Invoice.generate_uuid()
        
        subscription = Subscription.objects.filter(user = self.request.user).first()
        if subscription and subscription.active:
            amount = reduce_by(float(amount),20)
        paypal_dict = {
            'business':settings.PAYPAL_RECIEVER_EMAIL,
            'amount':amount,
            'item_name':item.item_name,
            'invoice':invoice_number,
            'currency_code':'USD',
            'notify_url':'http://{}{}'.format(host,reverse('paypal-ipn')),
            'cancel_url':'http://{}{}'.format(host,reverse('purchase_failed')),
            'return_url':'http://{}{}'.format(host,reverse('purchase_success',kwargs={'invoice_id':invoice_number})),
        }
        Invoice.objects.create(amount = paypal_dict['amount'],item_id = paypal_dict['invoice'],item_name=paypal_dict['item_name'],currency_code = 'USD',user=self.request.user).save()
        paypal_button = CustomPaypalButton(initial=paypal_dict)
        context['paypal_btn'] = paypal_button
        context['item_name'] = item.item_name
        context['amt'] = item.amount
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
        context['price'] = item.amount
        return context


class PostDetailView(DetailView):
    template_name = "post_detail.html"
    model = Post
    context_object_name = "post"  

    def get_queryset(self):
        qs = super().get_queryset()
        if self.kwargs.get('slug'):
            qs = qs.filter(slug = self.kwargs.get('slug'))
        return qs
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
        context['post_slug'] = self.get_object(self.queryset).slug
        return context


class BlogListView(ListView):
    template_name = 'blog.html'
    queryset = Post.objects.all()
    context_object_name = "post"
    paginate_by = 5
    
    def get_queryset(self) -> QuerySet[Any]:
        qs =  super().get_queryset()
        return qs
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
        return context

# * PURCHASE VIEWS

class PricingView(TemplateView):
    template_name = "pricing.html"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        invoice_number = Invoice.generate_uuid()
        subscriptions = Subscription.objects.all()
        try:
            context['subscription_active'] = subscriptions.get(user=self.request.user)
        except:
            context['subscription_active'] = False
        context['subscribtions'] = Store.objects.filter(item_name__icontains = 'plan')
        
        # get payment buttons
        qs = Store.objects.all().filter(item_name__icontains="plan")
        #todo generate paypal btn for the first and second plan then use it on the template by replacing existin btn
        game_plan = qs.filter(item_name__icontains="game").first()
        hackers_plan = qs.filter(item_name__icontains="hack").first()
        invoice_number = Invoice.generate_uuid()
        # replace these buttons with buttons that redirect to the confirm purchase page
        game_plan_purchase = game_plan.item_id
        
        hacker_plan_purchase = hackers_plan.item_id
        
        # append form buttons to context data 
        context.update({'game_plan_btn':game_plan_purchase,'hackers_plan_btn':hacker_plan_purchase})
        return context
    


def get_invoice(request,invoice_id):
    invoice = Invoice.objects.filter(item_id=invoice_id).first()
    context = {'invoice':invoice}
    try:
        context['subscription_active'] = Subscription.objects.get(user=request.user).active
    except:
        context['subscription_active'] = False
    return render(request,'invoice.html',context)


@login_required
def purchase_succesful(request,invoice_id=None):
    discount = None
    qs = get_object_or_404(Invoice,pk=invoice_id)

    if invoice_id:
    
        if 'unban' in qs.item_name:
            send_unban_mail(request.user.email)
            
        store_item = Store.get_by_invoice(qs)

        discount = get_discount(store_item.amount,qs.amount)
        context = {
            'invoice':qs,
            'discount':discount,
            'cost':store_item.amount
        }
        try:
            context['subscription_active'] = Subscription.objects.get(user=request.user)
            return render(request,'invoice.html',context)

        except:
            context['subscription_active'] = False
            return render(request,'invoice.html',context)

    else:
        return render(request,'invoice.html',{})



class PurchaseCancelledView(LoginRequiredMixin,TemplateView):
    template_name = 'purchases/cancelled.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
        return context
    
# * AUTHENTICATION

class AuthenticateView(View,TemplateResponseMixin):
    template_name = 'signup.html'
    model = User

    def get(self,request,*args, **kwargs):
        context = dict()
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
        return render(request,self.template_name,context)
    
    
    def post(self, request: HttpRequest,*args, **kwargs) -> HttpResponse:
        mode = self.kwargs.get('mode')
        if mode == 'signin':
            # handle signin
            username_or_email = request.POST['username_or_email']
            password = request.POST['password']
            if '@' in str(username_or_email) or '.com' in str(username_or_email):
                user = authenticate(request=request,email = username_or_email,password=password)
            else:
                user = authenticate(username = username_or_email,password=password)
            if user is not None:
                login(request,user)
                return redirect('index')
            else:
                # return msg based on error
                messages.error(request,'invalid information')
                return redirect('auth')
            
        elif mode == 'signup':
            # handle sign up
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            password2 = request.POST['password2']
            
            #* check if user with email or username already exists
            if User.objects.filter(email=email).exists():
                    messages.error(request,'Account with this email address already exists')
                    return redirect('auth')
            elif User.objects.filter(username=username).exists():
                messages.error(request,'Usernme taken')
                return redirect('auth')
            
            
            if username and email:
                if password == password2:
                    new_user = User.objects.create_user(username=username,password=password,email=email)
                    new_user.save()
                    login(request,new_user)
                    return redirect('index')
                else:
                    # passwords dont match
                    messages.error(request,'passwords dont match')
                    return redirect('auth')

        else:
            raise Http404
        return super().post(request, *args, **kwargs)


class ForgotPasswordView(TemplateView):
    template_name = 'forgot_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['subscription_active'] = Subscription.objects.get(user=self.request.user).active
        except:
            context['subscription_active'] = False
        return context
    


class TopUpView(ListView):
    template_name = 'topup.html'
    queryset = Store.objects.filter(item_name__icontains = 'gems')
    context_object_name = 'data'
    
    

@login_required
def confirm_payment(request:HttpRequest,item_id):
    # get purchase item and generate an invoice forthe item with paid set to false render the final purchase button to the template
    item = Store.objects.get(item_id = item_id)
    invoice_id = Invoice.generate_uuid()
    purchase_btn = generate_form_btn(item.amount,request.user,item.item_name,invoice_id,request.get_host())
    new_invoice = Invoice.objects.create(amount =item.amount ,item_id = invoice_id,item_name=item.item_name,currency_code = 'USD',user= request.user)
    new_invoice.save()

    context = {
        'purchase_btn':purchase_btn,
        'item':item
    }
    try:
        context['subscription_active'] = Subscription.objects.get(user=request.user)
    except:
        context['subscription_active'] = False
    finally:
        context['price'] = item.amount
        context['invoice'] = new_invoice
        
        return render(request,'purchases/confirm.html',context)