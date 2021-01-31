from django.shortcuts import render
from . forms import KakeiboForm
from django.urls import reverse_lazy
# Create your views here.
#ここから下を追加
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Category, Kakeibo
from django.db import models
from django.db.models import Sum
import calendar

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
# 月々のカテゴリ別の使用金額を折れ線グラフで表示
def show_line_graph(request):

    kakeibo_data=Kakeibo.objects.all()

    #カテゴリリストデータの生成
    category_list=[]
    category_data =Category.objects.all().order_by('-category_name')
    for item in category_data:
        category_list.append(item.category_name)
    date_list=[]
    for i in kakeibo_data:
        date_list.append((i.date.strftime('%Y/%m/%d')[:7]))
        date_list.sort()
    #重複値の除外
    x_label = list(set(date_list))
    x_label.sort(reverse=False)

    #月毎&カテゴリー毎の合計金額データセット
    monthly_sum_data=[]
    for i in range(len(x_label)):
        year,month = x_label[i].split("/")
        month_range = calendar.monthrange(int(year),int(month))[1]
        first_date = year + '-'+month + '-'+'01'
        last_date =year +'-'+month+'-'+str(month_range)
        #１ヶ月分のデータ
        total_of_month =Kakeibo.objects.filter(date__range=(first_date,last_date))
        category_total = total_of_month.values('category').annotate(total_price=Sum('money'))
    for j in range(len(category_total)):
        money =category_total[j]['total_price']
        category =Category.objects.get(pk=category_total[i]['category'])
        monthly_sum_data.append([x_label[i],category.category_name,money])

    #折れ線グラフのボーダーカラー
    border_color_list = ['254,97,132,0.8', '54,164,235,0.8', '0,255,65,0.8', '255,241,15,0.8',
                        '255,94,25,0.8', '84,77,203,0.8', '204,153,50,0.8', '214,216,165,0.8',
                        '33,30,45,0.8', '52,38,89,0.8']
    border_color =[]
    for x,y in zip(category_list, border_color_list):
        border_color.append([x,y])

    background_color_list = ['254,97,132,0.5', '54,164,235,0.5', '0,255,65,0.5', '255,241,15,0.5',
                            '255,94,25,0.5', '84,77,203,0.5', '204,153,50,0.5', '214,216,165,0.5'
                            '33,30,45,0.5', '52,38,89,0.5']
    background_color=[]
    for x,y in zip(category_list,background_color_list):
        background_color.append([x,y])

    matrix_list=[]
    for item_label in x_label:
        for item_category in category_list:
            matrix_list.append([item_label,item_category,0])
    """ matrix_listとmonthlysum_dataに対して、「年月+カテゴリ」の
        組み合わせが一致する要素に対してmatrix_listの金額（０円）を
        monthly_sum_dataの金額で上書きする。
    """
    for yyyy_mm,category,total in monthly_sum_data:
            for i,data in enumerate(matrix_list):
                if data[0]==yyyy_mm and data[1] ==category:
                    matrix_list[i][2] = total
    return render(request,'kakeibo/kakeibo_line.html',{
        'x_label':x_label,
        'category_list':category_list,
        'border_color':border_color,
        'background_color':background_color,
        'matrix_list':matrix_list,
    })