# Generated by Django 4.2.4 on 2023-08-25 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_store_id_store_item_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=150)),
                ('reply', models.TextField(max_length=200)),
            ],
            options={
                'db_table': 'Faq',
            },
        ),
    ]
