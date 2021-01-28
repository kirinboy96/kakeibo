from django.shortcuts import render
from . forms import KakeiboForm
from django.urls import reverse_lazy
# Create your views here.
#ここから下を追加
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Category, Kakeibo
from django.db import models

#一覧表示用のDjango標準ビュー(ListView)を承継して一覧表示用のクラスを定義
class KakeiboListView(ListView):
   #利用するモデルを指定
   model = Kakeibo
   # データを渡すテンプレートファイルを指定
   template_name = 'kakeibo/kakeibo_list.html'

   #家計簿テーブルの全データを取得するメソッドを定義
   def queryset(self):
       return Kakeibo.objects.all()

class KakeiboCreateView(CreateView):
    model = Kakeibo
    form_class = KakeiboForm
    success_url =  reverse_lazy('kakeibo:create_done')

def create_done(request):
    return render(request,'kakeibo/create_done.html')

class KakeiboUpdateView(UpdateView):
    model = Kakeibo
    form_class = KakeiboForm
    success_url = reverse_lazy('kakeibo:update_done')

def update_done(request):
    return render(request,'kakeibo/update_done.html')

class KakeiboDeleteView(DeleteView):
    model = Kakeibo
    success_url = reverse_lazy('kakeibo:delete_done')

def delete_done(request):
    return render(request,'kakeibo/delete_done.html')


def show_circle_graph(request):
    # 全データ取得
    kakeibo_data = Kakeibo.objects.all()

    # すべての金額の合計を求める
    total = 0
    for item in kakeibo_data:
        total += item.money

    category_list = []
    # 全カテゴリ名をテーブルから取得する。
    category_data = Category.objects.all()
    # ループ処理でカテゴリ名のリストを作成する。
    for item in category_data:
        category_list.append(item.category_name)
    # つづいてカテゴリ毎の合計金額を求める
    category_dict = {}
    for i, item in enumerate(category_list):
        category_total = Kakeibo.objects.filter(category__category_name=category_list[i]).aggregate(sum=models.Sum('money'))['sum']
        # 割合を計算する
        if category_total != None:
            ratio = int((category_total / total) * 100)
            category_dict[item] = ratio
        else:
            ratio = 0
            category_dict[item] = ratio

    return render(request, 'kakeibo/kakeibo_circle.html', {
        'category_dict': category_dict,
    })