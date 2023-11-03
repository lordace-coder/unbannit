from datetime import datetime, timedelta
from functools import reduce
from itertools import accumulate

from core.exceptions import UserSubscriptionError
from core.mails import send_gmail, send_unban_mail
from core.models import Comments, Invoice, MembershipToken, Post, Subscription
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest
from django.urls import reverse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import (ListAPIView, ListCreateAPIView,
                                     RetrieveAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Token, UnbanActive
from .permissions import StaffOnly
from .serializers import CommentSerializer, InvoiceSerializer, PostSerializer


class CreateCommentApiView(ListCreateAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer
    
    def get_queryset(self):
       
        slug  = self.kwargs.get('slug')
        post = Post.objects.get(slug=slug)
        qs = super().get_queryset().filter(post = post)
        
        return qs


# todo work on responses

@api_view(['POST'])
def ForgotPasswordApiView(request):
    # check if account with this email 
    email = request.data.get('email')

    acct = User.objects.filter(email = email)
    if acct.exists():
        # add email to session data
        request.session['verify_email'] = email
        request.session.modified = True

        Token.generate_token(email)

        return Response(status = 200)
    else:
        return Response(status=404)




@api_view(['POST'])
def VerifyTokenApiView(request):
    token = request.data.get('token')
    new_password = request.data.get('password')
    email = request.session.get('verify_email')
    verified = Token.verify_token(email,token)


    if email and verified:
        user = User.objects.filter(email = email).first()
        user.set_password(new_password)
        user.save()

        return Response(status=200)
    else:
        return Response(status=404)

@api_view(['GET'])
def handle_unban_msg(request,email):
    if not '@' in email:
        email = request.user.email
        request.session['unban_email'] = email
        request.session.modified = True
    return Response()


@api_view(['GET'])
def create_membership_token(request):
    if not request.user.is_authenticated:
        return Response('user isnt logged in')
    
    
    user = request.user
    token = None

    try:
        token = MembershipToken.generate_token(user)
        return Response({'token':token},status=200)
    except UserSubscriptionError:
        data = {'error':'user has no active subscription'}
        return Response(data=data,status = 404)

@api_view(['GET'])
def verify_membership_token(request,token):
    qs = MembershipToken.objects.filter(token = token).exists()
    if qs:
        return Response(status = 200)
    else:
        return Response(status = 404)



#* invoices
class InvoiceListApiView(ListAPIView):
    authentication_classes = []
    # permission_classes = [StaffOnly]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all().filter(paid=True)



class InvoiceDetailApiView(RetrieveAPIView):
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication
    ]
    permission_classes = [StaffOnly]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()


# *posts
class PostApiView(ListCreateAPIView):
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication
    ]
    permission_classes = [StaffOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class PostDetailUpdateApiView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication
    ]
    permission_classes = [StaffOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    
    def get_object(self):
        try:
            obj = self.get_queryset().get(slug = self.kwargs.get('slug'))
        except:
            raise Http404
        print(obj)
        return obj



@api_view(['GET'])
def meta_data_view(request):
    users_count = User.objects.all().count()
    
    # total sales
    invoices = Invoice.objects.filter(paid=True).values_list('amount')
    reducer = lambda x,y:x+y
    qs = reduce(reducer,invoices)
    qs = reduce(reducer,qs)

    # post count
    post_count = Post.objects.all().count()
    
    data = {
        'users':users_count,
        'total-sales':f"${qs}",
        'total-posts':post_count
    }
    return Response(data)


@api_view(['GET'])
def get_all_urls(request:HttpRequest):
    generate_path = lambda x:request.build_absolute_uri(reverse(x))
    data = {
        'host':request.get_host(),
        'api-urls':generate_path('get-all-urls'),
        'all-posts':generate_path('posts-api-view'),
        'single-post':f"{generate_path('posts-api-view')}<slug>",
        'all-invoices':generate_path('invoices-api-view'),
        'single-invoice':f"{generate_path('invoices-api-view')}<item_id>",
        'meta-data':generate_path('meta-data'),
        'verify-membership-token':f"{generate_path('generate-membership-token-view')}<token>",
        # auth views
        'get-token':generate_path('token_obtain_pair'),
        'refresh-token':generate_path('token_refresh'),
        'verify-token':generate_path('verify-token'),
        'clear-invoices':generate_path('clear-invoice'),
        'send-custom-mail':f"{generate_path('get-all-urls')}send-custom-mail/<id>"
    }
    
    return Response(data)


@api_view(['GET'])
def delete_unpaid_invoices(request):
    if request.user.is_authenticated and request.user.is_staff:
        # *check all invoices that has been unpaid for over 2 weeks
        qs = Invoice.objects.filter(paid=False)
        for i in qs:
            time_diff = datetime.now() - i.created_at
            if time_diff >= timedelta(weeks=3):
                i.delete()
        return Response({'detail':'completed'},status=200)
    return Response({'detail':'permission denied'},status=403)


@api_view(['POST'])
def send_custom_mail(request,id):
    recipent = User.objects.get(id = id)
    print('posted data',request.data)
    subject = request.data['subject']
    message = request.data['message']
    print({
        'subject':subject,
        'message':message,
        'email-address':recipent.email
    })
    
    try:
        recipent.email_user(subject=subject,message=message,from_email=settings.EMAIL_HOST_USER)
        return Response(status=200,data="email sent successfully")
    except Exception as e:
        return Response(status=404,data={'error':f"{e}"})



@api_view(['GET'])
def get_time_left(request):
    if not request.user.is_authenticated:
        return Response()
    user = request.user
    qs = UnbanActive.objects.filter(user = user)
    if qs.exists() and not qs.first().is_unbanned:
        return Response({'username':user.username,'time':qs.first().time_left()})
    else:
        return Response(status = 404)



@api_view(['GET'])
def handle_users_payment(request,invoice_id,email=None):
    try:
        invoice:Invoice = Invoice.objects.get(invoice_id)
        if 'unban' in invoice.item_name:
                qs = UnbanActive.objects.filter(user = invoice.user)
                if not qs.exists():
                    unban_service = UnbanActive.objects.create(user = invoice.user)
                    unban_service.save()
                send_unban_mail(invoice.user.email)
        invoice.paid = True
        return Response(status = 200)
    except Exception as e:
        return Response(status = 400,data={'error':f"{e}"})