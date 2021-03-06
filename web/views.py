from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect,render_to_response
from django.urls import reverse
from django.contrib import auth, messages
from django.contrib.auth.hashers import *
from django.contrib.auth.forms import PasswordChangeForm
from web.models import UserImage,History,User
from web.forms import HistoryForm
from web import forms
import os
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from license.settings import BASE_DIR
from web.forms import RegisterForm, LoginForm, UserChangeForm
from django.http import HttpResponse, HttpResponseRedirect
import json


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', context={
            'form': LoginForm(),
        })
    else:
        form = LoginForm(data=request.POST, request=request)  # 需要传的参数是data+request， 只传data是不够的!
        if form.is_valid():  # LoginForm继承了AuthenticationForm, 会自动完成认证
            auth.login(request, form.get_user())
            # 将用户登陆
            redirect_to = request.GET.get(key='next', default=reverse('web:personal'))  # 重定向到要访问的地址，没有的话重定向到首页
            return HttpResponseRedirect(redirect_to)
        else:  # 认证失败
            return render(request, 'login.html', context={
                'form': form
            })


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', context={'form': RegisterForm()})
    else:
        print(request.POST.get('username'))
        form = RegisterForm(request.POST)
        if form.is_valid():  # RegisterForm继承了UserCreationForm， 会完成用户密码强度检查，用户是否存在的验证
            try:
                form.save(True)  # 认证通过。直接保存到数据库
                url = reverse('web:login')
                return HttpResponseRedirect(url)
            except:
                messages.error(request,'您的邮箱已注册!')
                url = reverse('web:signup')
                return HttpResponseRedirect(url)
        else:
            return render(request, 'signup.html', context={'form': form})


def index(request):
    # return HttpResponseRedirect('')
    return render(request, 'index.html', {})


def introduction(request):
    return render(request, 'introduction.html', {})


def team(request):
    return render(request, 'team.html', {})


def download(request):
    return render(request, 'download.html', {})


def contact(request):
    return render(request, 'contact.html', {})


def user(request):
    return render(request, 'user.html', {})


def forgot(request):
    return render(request, 'forgot.html', {})




@login_required
def apply(request):
    user_images = UserImage.objects.filter(user=request.user)
    if len(user_images) > 0:
        return render(request, 'apply.html', {})
    else:
        messages.error(request, '无法申请,请您上传工作证和扫描件！')
        return redirect('web:upload')


def new_apply(request):
    user_history=History.objects.filter(user=request.user,examine="未审核")
    SNnum_input=request.GET.get('SNnum')
    print(SNnum_input)
    if len(user_history) == 0 :
        new_history=History()
        new_history.user=request.user
        new_history.SNnum=SNnum_input
        new_history.save()
        for_activation_history=History.objects.get(user=request.user,examine="未审核",SNnum=SNnum_input)
        a=str(for_activation_history.id)
        cur_path = os.path.abspath(os.curdir)
        print(a)
        path = cur_path + r'\web\static\activation\history_id_'+a
        os.mkdir(path)
    #     messages.success(request, '申请成功!')
    #     return redirect('web:apply')
    # else :
    #     messages.error(request, '您的申请正在处理,请耐心等待！')
    #     return redirect('web:apply')
    user_history2=History.objects.filter(user=request.user,SNnum=SNnum_input,examine="未审核")
    length_no_examine=len(user_history2)
    response_data = {'len':length_no_examine}  #如果申请成功就是1,申请失败则是0
    return HttpResponse(json.dumps(response_data), content_type="application/json") 

def new_apply_delete(request):
    user_history_delete=History.objects.filter(user=request.user,examine="未审核")
    if len(user_history_delete) == 1 :
        user_history_delete.delete()
        messages.success(request, '撤销成功！')
        return redirect('web:apply')
    elif len(user_history_delete) == 0 :
        messages.error(request, '您没有可撤销的申请!')
        return redirect('web:apply')
    else :
        messages.error(request, '出现未知错误,请联系管理员')
        return redirect('web:apply')
        


def allow_examine(request):
    history_id_allow=request.GET.get('allow_history_id')
    user_history=History.objects.get(id=history_id_allow)
    user_history.examine="审核通过"
    user_history.save()
    response_data = {'examine':user_history.examine}  
    return HttpResponse(json.dumps(response_data), content_type="application/json")  
   
def cancel_examine(request):
    history_id_cancel=request.GET.get('cancel_history_id')
    user_history=History.objects.get(id=history_id_cancel)
    user_history.examine="未通过"
    user_history.save()
    response_data = {'examine':user_history.examine}  
    return HttpResponse(json.dumps(response_data), content_type="application/json")  

# def changecss(request):
#     history_id_change=request.GET.get('change_history_id')
#     user_history=History.objects.get(id=history_id_change)
#     user=User.objects.get(username=user_history.username)
#     personal_historys=History.objects.filter(user = user)
#     response_data = {'personal_historys':personal_historys}
#     return HttpResponse(json.dumps(response_data), content_type="application/json")  
   



@login_required
def personal(request):
    admin=User.objects.get(username="admin@123.com")
    if admin==request.user:
        return redirect('web:administrator')
    else:
        history_form=forms.HistoryForm()  
        personal_historys=History.objects.filter(user = request.user)
        return render(request, "personal.html",context={"personal_historys": personal_historys})



def administrator(request):
    admin=User.objects.get(username="admin@123.com")
    if admin==request.user:
        history_form=forms.HistoryForm()   
        admin_historys=History.objects.filter(examine = "未审核")
        for history in admin_historys:
            user=history.user
            #print (user.name)
            user_images = UserImage.objects.filter(user = user)
            personal_historys=History.objects.filter(user = user,examine="审核通过"or"未通过")
            #print(personal_historys[0].user.id)
            history.user_image = user_images[0]
            history.personal_history = personal_historys
            #print(admin_historys[1].personal_history[0].user)
        return render(request, "administrator.html",context={"admin_historys": admin_historys})
    else :
        messages.error(request, '您没有进入管理员界面的权限!')
        return redirect('web:personal')

@login_required
@transaction.atomic
def change(request):
    if request.method == 'GET':
        return render(request, 'change.html', context={'form': UserChangeForm(instance=request.user)})
    else:
        user_form = UserChangeForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, '修改成功！')
            return redirect('web:change')
        else:
            messages.error(request, '修改失败，请完善所有信息！')
            return redirect('web:change')


@login_required
def password_change(request):
    if request.method == 'GET':
        form = PasswordChangeForm(request.user)
        return render(request, 'passwordChange.html', context={'form': form})
    else:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save(commit=True)
            update_session_auth_hash(request, user)
            messages.success(request, '密码修改成功！')
            return redirect('web:personal')

        else:
            messages.error(request, '密码修改失败！')
            return redirect('web:passwordChange')

@login_required
def upload_file(request):
    def file_save(file, username, path):
        upload_filename = file.name
        upload_file_type = upload_filename.split('.')[-1]
        save_image_name = username + '.' + upload_file_type
        upload_file_path = os.path.join(BASE_DIR, 'web', 'static', 'images', path, save_image_name)
        with open(upload_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return "images/{}/".format(path) + save_image_name

    def handle_uploaded_file(file_photo, file_scanning_copy, username, user):
        user_image = UserImage.objects.filter(user=user)
        static_image_path = file_save(file_photo, username, 'photo')
        static_scanning_copy_path = file_save(file_scanning_copy, username, 'scanning_copy')
        if len(user_image) == 1:
            user_image[0].user_image_path = static_image_path
            user_image[0].user_scanning_copy_path = static_scanning_copy_path
            user_image[0].save()
        else:
            user_image = UserImage(user=user, user_image_path=static_image_path,
                                   user_scanning_copy_path=static_scanning_copy_path)
            user_image.save()

    if request.method == 'GET':
        return render(request, 'upload.html', context={})
    else:
        print('ok1')
        handle_uploaded_file(request.FILES['scanning_copy_file'],request.FILES['photo_file'], request.user.username, request.user)
        messages.success(request, '工作证上传成功！')
        return redirect('web:upload')


def upload(request):
    return render(request, 'upload.html', {})





def edit_action(request):
    pass


def logout(request):
    auth.logout(request)
    redirect_to = '/'
    return HttpResponseRedirect(redirect_to)
