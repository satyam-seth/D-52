from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils import timezone
from .forms import RecordFrom,WaterFrom
from .models import Record,Water

# Create your views here.

def add(request):
    fm1=RecordFrom(label_suffix='')
    fm2=WaterFrom(label_suffix='')
    context={'add_active':'active','add_disabled':'disabled','form1':fm1,'form2':fm2}
    return render(request,'data/add.html',context)

def add_item(request):
    if request.method=='POST':
        fm=RecordFrom(request.POST)
        if fm.is_valid():
            dt=fm.cleaned_data['date']
            nm=fm.cleaned_data['name']
            it=fm.cleaned_data['item']
            pr=fm.cleaned_data['price']
            current_dt=timezone.now()
            reg=Record(date=dt,name=nm,item=it,price=pr,datetime=current_dt)
            reg.save()
            messages.success(request,'Your item record successfully added.')
        return redirect('add')

def add_water(request):
    if request.method=='POST':
        fm=WaterFrom(request.POST)
        if fm.is_valid():
            dt=fm.cleaned_data['date']
            qt=fm.cleaned_data['quantity']
            current_dt=timezone.now()
            reg=Water(date=dt,quantity=qt,datetime=current_dt)
            reg.save()
            messages.success(request,'Water record successfully added.')
        return redirect('add')

def records(request):
    records=Record.objects.all().order_by('date')
    waters=Water.objects.all().order_by('date')
    context={
        'records_active':'active',
        'records_disabled':'disabled',
        'records':records,
        'waters':waters}
    return render(request,'data/records.html',context)

def detailed_view(request,var):
    if var=='satyam':
        data=Record.objects.filter(name='Satyam Seth').order_by('date')
        
    elif var=='ankit':
        data=Record.objects.filter(name='Ankit Kumar Gupta').order_by('date')
        
    elif var=='ganga':
        data=Record.objects.filter(name='Ganga Sagar Bharti').order_by('date')
     
    elif var=='prashant':
        data=Record.objects.filter(name='Prashant Kumar Yadav').order_by('date')
     
    else:
        data=Water.objects.all().order_by('date')

    return render(request,'data/detailed.html',{'records':data,'var':var})

def report(request):
    context={'report_active':'active','report_disabled':'disabled'}
    return render(request,'data/report.html',context)

def download(request):
    return render(request,'data/download.html')