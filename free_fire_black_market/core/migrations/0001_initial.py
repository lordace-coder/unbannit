# Generated by Django 4.2.4 on 2023-08-18 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('post', models.TextField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to='posts/images')),
                ('image_2', models.ImageField(blank=True, null=True, upload_to='posts/images')),
            ],
        ),
    ]
