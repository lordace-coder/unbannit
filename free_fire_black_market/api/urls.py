from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from . import views

urlpatterns = [
        # get urls
    path('',views.get_all_urls,name='get-all-urls'),
    path('time-left',views.get_time_left,name='time-left'),
    path('comments/<slug:slug>',views.CreateCommentApiView.as_view()),
    path('forgot_password/',views.ForgotPasswordApiView,name='recover-password'),
    path('forgot_password/verify_token',views.VerifyTokenApiView,name='verify-password-token'),
    path('request-unban/',views.handle_unban_msg,name='send_unban_mail'),
    path('request-unban/<str:email>',views.handle_unban_msg),
    path('membership-token-generate/',views.create_membership_token,name="generate-membership-token-view"),
    path('membership-token-generate/<slug:token>',views.verify_membership_token,name='verify-membership-token'),
    path('invoices/',views.InvoiceListApiView.as_view(),name='invoices-api-view'),
    path('invoices/<slug:pk>',views.InvoiceDetailApiView.as_view()),
    path('posts/',views.PostApiView.as_view(),name='posts-api-view'),
    path('posts/<slug:slug>',views.PostDetailUpdateApiView.as_view()),
    path('info/',views.meta_data_view,name='meta-data'),
    path('clear_invoice_db/',views.delete_unpaid_invoices,name='clear-invoice'),
    
    # * TOKEN VIEWS
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/',TokenVerifyView.as_view(),name='verify-token'),
    
    # * HELPER VIEWS
    path('send-custom-mail/<int:id>',views.send_custom_mail,name='send-mail')
]

