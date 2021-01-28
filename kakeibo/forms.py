from django import forms
from .models import Kakeibo

class KakeiboForm(forms.ModelForm):
    # 新規データの登録画面
    class Meta:
        model = Kakeibo
        fields = ["date","category","money","memo"]


