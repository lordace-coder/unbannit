from django.contrib import admin

from .models import (FAQ, Comments, Invoice, MembershipToken, Post, Store,
                     Subscription)


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ['id','title','created_at']
    fields = ['title','created_at','post','slug','image']


admin.site.register(Post,PostAdmin)
admin.site.register(Comments)
admin.site.register(Store)
admin.site.register(FAQ)
admin.site.register(Invoice)
admin.site.register(Subscription)
admin.site.register(MembershipToken)