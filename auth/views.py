from django.shortcuts import render,redirect
from analysis.models import Profile,Plan_purchase
from .forms import SignUpForm,UserUpdateForm,ProfileUpdateForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utlis import generate_token
from django.core.mail import EmailMessage
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
#function base view
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            instance=form.save()
            user=User.objects.get(id=instance.id)
            user.is_active=False
            user.save()
            email_subject="Activate Your Account"
            message=render_to_string('activate.html',{
            'user':user,
            'domain':'http://127.0.0.1:8000',            
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)

        })
            email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[request.POST.get('email')])
            email_message.send()
            return redirect('emailverification')
    else:
        form = SignUpForm()
    return render(request, 'login.html', {'form': form})
       
def emailverification(request):
    return render(request, 'verification.html')

def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('/')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile_edit.html',context)
 #class base view   
class ActtivateAccountView(View):
     def get(self,request,uidb64,token):
            try:
                uid=force_str(urlsafe_base64_decode(uidb64))
                user=User.objects.get(pk=uid)
            except Exception as identifier:
                 user=None
            if user is not None and generate_token.check_token(user,token):
               user.is_active=True
               user.save()
               return redirect('emailconfirm')
            else:
                return redirect('activate_fail')

 
def emailconfirm(request):
    return render(request,'activated.html')
def activate_fail(request):
    return render(request,'activatefail.html')
   
# def User_profile(request):
#     if request.htmx:
#         return render(request,'components/User_profile.html')
#     else:
#         return render(request,'User_profile.html')
# View function to display user profile
def profile(request):
    # Check if user activity needs to be traced, redirect if necessary
    # trace = track_user_activity(request)
    # if trace == True:
    #     return redirect('account_restriction')
    # trace2=UserMonitering.objects.filter(user=request.user)
    
    # # Check if request is from a proxy, redirect if necessary
    # check = proxy_checker(request)
    # if check == True:
    #     return redirect('proxy_warning_view')
    
    # Retrieve user profile data
    data = Profile.objects.get(user=request.user)
    
    # Check if user commission is zero
    # usercommession = data.commession == 0
    
    # Retrieve total balance of the user
    # totalbalance = data.balance
    
    # Retrieve current user profile
    currentuser = Profile.objects.filter(user=request.user)
    
    # Render profile template with relevant data
    # return render(request, 'profile.html', {'currentuser': currentuser, 'usercommession': usercommession, 'totalbalance': totalbalance})
    return render(request, 'profile.html', {'currentuser': currentuser})

def edit_profile(request):
    # Check if user activity needs to be traced, redirect if necessary
    # trace = track_user_activity(request)
    # if trace == True:
    #     return redirect('account_restriction')
    
    # Check if request is from a proxy, redirect if necessary
    # check = proxy_checker(request)
    # if check == True:
    #     return redirect('proxy_warning_view')
    
    # Retrieve user profile data
    data = Profile.objects.get(user=request.user)
    
    # Retrieve total balance of the user
    # totalbalance = data.balance
    
    # # Check if user commission is zero
    # usercommession = data.commession == 0
    
    if request.method == 'POST':
        # If request method is POST, process form data
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('/auth/profile')
    else:
        # If request method is GET, render form with existing data
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # Prepare context to pass to the template
    context = {
        'u_form': u_form,
        'p_form': p_form,
        # 'usercommession': usercommession,
        # 'totalbalance': totalbalance
    }

    # Render edit profile template with form data
    return render(request, 'editprofile.html', context)

def Analytical(request):
    return render(request,'AnalyticalDashboard.html')

def Purchases(request):
    purchases = Plan_purchase.objects.all()
    context = {
    'purchases':purchases
    }
    
    return render(request,'Purchases.html', context)
def Reports(request):
    return render(request,'Reports.html')
def Help(request):
    return render(request,'Help.html')

def deactivate_subscription(request):
    if request.method == "POST":
        subscription_id = request.POST.get("subscription_id")
        subscription = get_object_or_404(Plan_purchase, id=subscription_id)
        
        if subscription.status != "Inactive":
            subscription.status = "Inactive"
            subscription.save()

        
        return redirect("User_Purchases")  

def activate_subscription(request):
    if request.method == "POST":
        subscription_id = request.POST.get("subscription_id")
        subscription = get_object_or_404(Plan_purchase, id=subscription_id)
        
        if subscription.status != "Active":
            subscription.status = "Active"
            subscription.save()

        return redirect("User_Purchases")  
