# Generated by Django 4.0.1 on 2022-01-23 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Order received', 'Order received'), ('Baking', 'Baking'), ('Baked', 'Baked'), ('Out for delivery', 'Out for delivery'), ('Order completed', 'Order completed')], default='Order Recieved', max_length=100),
        ),
    ]
