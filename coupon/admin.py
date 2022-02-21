from django.contrib import admin
from coupon.models import Coupon, UserCoupon
# Register your models here.

admin.site.register(Coupon)
admin.site.register(UserCoupon)