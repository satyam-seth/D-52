from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .forms import FeedbackFrom
from .models import Feedback,Electricity,Maid
from data.models import Record,Water

# Create your views here.

def home(request):
    w_sum=Water.objects.aggregate(Sum('quantity'))['quantity__sum']
    w_price=35*w_sum
    w_pp=w_price/4

    electricity=Electricity.objects.latest('due_date')
    e_pp=electricity.price/4
    
    maid=Maid.objects.latest('due_date')
    m_pp=maid.price/4
    days_left=(maid.due_date-timezone.now().date()).days

    satyam_record=Record.objects.filter(name='Satyam Seth')
    st_price=satyam_record.aggregate(Sum('price'))['price__sum']
    st_items=len(satyam_record)

    ankit_record=Record.objects.filter(name='Ankit Kumar Gupta')
    at_price=ankit_record.aggregate(Sum('price'))['price__sum']
    at_items=len(ankit_record)

    ganga_record=Record.objects.filter(name='Ganga Sagar Bharti')
    gt_price=ganga_record.aggregate(Sum('price'))['price__sum']
    gt_items=len(ganga_record)

    prashant_record=Record.objects.filter(name='Prashant Kumar Yadav')
    pt_price=prashant_record.aggregate(Sum('price'))['price__sum']
    pt_items=len(prashant_record)

    context={
        'home_active':'active',
        'home_disabled':'disabled',
        'w_sum':w_sum,
        'w_price':w_price,
        'w_pp':w_pp,
        'electricity':electricity,
        'e_pp':e_pp,
        'maid':maid,
        'm_pp':m_pp,
        'days_left':days_left,
        'st_price':st_price,
        'st_items':st_items,
        'at_price':at_price,
        'at_items':at_items,
        'gt_price':gt_price,
        'gt_items':gt_items,
        'pt_price':pt_price,
        'pt_items':pt_items
        }

    return render(request,'core/index.html',context)

def about(request):
    context={
        'about_active':'active',
        'about_disabled':'disabled'
        }
    return render(request,'core/about.html',context)

def feedback(request):
    if request.method=='POST':
        fm=FeedbackFrom(request.POST)
        if fm.is_valid():
            nm=fm.cleaned_data['name']
            tp=fm.cleaned_data['problem']
            mg=fm.cleaned_data['message']
            current_dt=timezone.now()
            reg=Feedback(name=nm,problem=tp,message=mg,datetime=current_dt)
            reg.save()
            messages.success(request,'Thank you for your valuable feedback, it will help us to improve your experience.')
        return redirect('home')
    else:
        fm=FeedbackFrom()
    
    context={
        'feedback_active':'active',
        'feedback_disabled':'disabled',
        'form':fm
        }
    return render(request,'core/feedback.html',context)

def search(request):
    query=request.GET['query']
    if len(query)>50 or len(query)==0:
        results=Record.objects.none()
    else:
        results=Record.objects.filter(item__icontains=query)
    return render(request,'core/search.html',{'records':results})