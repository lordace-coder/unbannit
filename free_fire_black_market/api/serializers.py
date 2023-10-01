from core.models import Comments, Invoice, Post
from rest_framework import serializers


class CommentSerializer(serializers.ModelSerializer):
    time = serializers.CharField(source = 'get_formatted_time',read_only=True)
    post = serializers.SerializerMethodField()
    post_slug = serializers.CharField(write_only = True)
    
    class Meta:
        model = Comments
        fields = (
            'author',
            'comment',
            'time',
            'post',
            'post_slug'
        )

    def get_post(self,obj):
        post = obj.post.title
        return post

    def create(self, validated_data:dict):
        comment = None
        try:
            post_slug = validated_data.pop('post_slug')
            post = Post.objects.get(slug = post_slug)
            comment = Comments.objects.create(**validated_data)
            comment.post = post
            comment.save()
        except Exception as e:
            ...
        return comment



class InvoiceSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source = 'user.username')
    date = serializers.CharField(source='format_date')
    item = serializers.CharField(source = 'item_name')
    class Meta:
        model = Invoice
        fields = (
            'amount',
            'user',
            'paid',
            'item_id',
            'date',
            'item',
            'currency_code'
        )



class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ["id"]