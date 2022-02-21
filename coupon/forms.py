from django import forms
from utilities.query import get_object_or_none
from coupon.models import UserCoupon, Coupon
from django.core.exceptions import ValidationError


class UserCouponForm(forms.ModelForm):
    code = forms.CharField(max_length=50)
    
    class Meta:
        model = UserCoupon
        fields = ["code"]

    def clean_code(self):
        data = self.cleaned_data['code']
        coupon = get_object_or_none(Coupon, code=data)
        if coupon is None or coupon.active is None:
            raise ValidationError("Invalid Promo code")
        # self.cleaned_data['code'] = coupon.id
        # return self.cleaned_data
        return coupon

    # def clean(self):
    #     return self.cleaned_data
