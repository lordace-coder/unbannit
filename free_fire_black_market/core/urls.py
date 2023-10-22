from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('',views.HomeView.as_view(),name="index"),
    path('purchase-gems/',views.TopUpView.as_view(),name='topup'),
    path('purchase-gems/confirm/<slug:item_id>',views.confirm_payment,name='topup'),
    path('unban_acct/',views.UnbanAcctView.as_view(),name='purchase_acct'),
    path('unban_acct/handle_unban',views.HandleUnbanView.as_view(),name='handle-unban'),
    path('contact/',views.ContactPageView.as_view(),name='contact'),
    
    path('contact/<str:status>',views.ContactPageView.as_view(),name='contact'),
    
    path('tutorials/',views.TutorialPageView.as_view(),name='tutorials'),
    path('tutorials/<str:selected_tab>',views.TutorialPageView.as_view()),
    path('receipt/<slug:invoice_id>',views.get_invoice,name='invoice'),
    path('receipt/',views.get_invoice,name='invoice'),
    path('pricings/',views.PricingView.as_view(),name='pricing'),
    path('<slug:slug>',views.PostDetailView.as_view(),name="post"),
    path('blog/',views.BlogListView.as_view(),name="blog"),
    path('auth/',views.AuthenticateView.as_view(),name='auth'),
    path('auth/recovery',views.ForgotPasswordView.as_view(),name='forgot-password'),
    path('auth/<str:mode>',views.AuthenticateView.as_view()),
    
    # purchase views
    path('purchase-status/succesfull/<slug:invoice_id>',views.purchase_succesful,name='purchase_success'),
    path('purchase-status/cancelled',views.PurchaseCancelledView.as_view(),name='purchase_failed'),
]

urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)