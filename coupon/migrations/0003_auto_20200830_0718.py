# Generated by Django 2.2.2 on 2020-08-30 07:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coupon', '0002_auto_20200830_0613'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='valid_days',
            field=models.IntegerField(default=14),
        ),
        migrations.CreateModel(
            name='UserCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon_added', to='coupon.Coupon')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'UserCoupon',
                'verbose_name_plural': 'UserCoupons',
            },
        ),
    ]
