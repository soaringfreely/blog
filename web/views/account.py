#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json

from io import BytesIO
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from utils.check_code import create_validate_code
from repository import models
from ..forms.account import LoginForm, RegisterForm

def jsonp(request):
    func = request.GET.get('callback')
    content = '%s(100000)' %(func,)
    return HttpResponse(content)


def check_code(request):
    """
    验证码
    :param request:
    :return:
    """
    stream = BytesIO()
    img, code = create_validate_code()
    img.save(stream, 'PNG')
    request.session['CheckCode'] = code
    return HttpResponse(stream.getvalue())


def login(request):
    """
    登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        result = {'status': False, 'message': None, 'data': None}
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_info = models.UserInfo.objects. \
                filter(username=username, password=password). \
                values('nid', 'nickname',
                       'username', 'email',
                       'avatar',
                       'blog__nid',
                       'blog__site').first()
            print(user_info)
            if not user_info:
                # result['message'] = {'__all__': '用户名或密码错误'}
                result['message'] = '用户名或密码错误'
            else:
                result['status'] = True
                request.session['user_info'] = user_info
                if form.cleaned_data.get('rmb'):
                    request.session.set_expiry(60 * 60 * 24 * 7)
        else:
            print(form.errors)
            if 'check_code' in form.errors:
                result['message'] = '验证码错误或者过期'
            else:
                result['message'] = '用户名或密码错误'
        return HttpResponse(json.dumps(result))


def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.method == 'GET':
        # models.UserInfo.objects.create(
        #     username='fan1',
        #     password='123',
        #     email='hurte@ccc.com',
        # )
        obj = RegisterForm()
        return render(request, 'register.html', {'obj': obj})
    elif request.method == 'POST':
        err = None
        emailerr = None
        obj = RegisterForm(request.POST)
        if obj.is_valid():
            print(obj.cleaned_data)
            if obj.cleaned_data.get('password') != obj.cleaned_data.get('password2'):
                err = '两次密码不一致'
            else:
                # obj = models.UserInfo.objects.filter(**obj.cleaned_data)
                try:
                    ret = models.UserInfo.objects.create(
                        username=obj.cleaned_data.get('username'),
                        password=obj.cleaned_data.get('password'),
                        email=obj.cleaned_data.get('email'),

                    )
                except Exception as e:
                    print(e)
                    emailerr = '邮箱已存在'
                return redirect('/login.html/')
        else:
            print(obj.errors)
        return render(request, 'register.html', {'obj': obj, 'err': err, 'emailerr': emailerr})


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.clear()

    return redirect('/')
