#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import json
import uuid
from django.shortcuts import render
from django.shortcuts import HttpResponse,Http404
from django.shortcuts import redirect
from django.db import transaction
from django.urls import reverse

from ..forms.article import ArticleForm
from ..forms.userinfo import UserInfoForm
from ..auth.auth import check_login
from repository import models
from utils.pagination import Pagination
from utils.xss import XSSFilter


@check_login
def index(request):
    return render(request, 'backend_index.html')


@check_login
def base_info(request):
    """
    博主个人信息
    :param request:
    :return:
    """
    if request.method == 'GET':
        data = models.UserInfo.objects.filter(nid=request.session.get('user_info').get('nid')).values(
            'nickname',
            'blog__site',
            'blog__theme',
            'blog__title',
            'avatar'
        ).first()
        print(data)
        obj = UserInfoForm(initial={
            'nickname': data.get('nickname'),
            'site': data.get('blog__site'),
            'theme': data.get('blog__theme'),
            'title': data.get('blog__title')
        })
        return render(request, 'backend_base_info.html', {'obj': obj})
    elif request.method == 'POST':
        # 修改用户信息
        obj = UserInfoForm(request.POST)
        if obj.is_valid():
            print(obj.cleaned_data)
            print(request.session.get('user_info'))
            nid = request.session.get('user_info').get('nid')
            data = models.UserInfo.objects.filter(nid=nid).first()
            data.nickname = request.POST.get('nickname')
            try:
                data.blog.site = request.POST.get('site')
                data.blog.theme = request.POST.get('theme')
                data.blog.title = request.POST.get('title')
                data.blog.save()
                request.session['user_info']['blog__site'] = request.POST.get('site')
            except:
                blog = models.Blog.objects.create(user=data,
                                                  site=request.POST.get('site'),
                                                  theme=request.POST.get('theme'),
                                                  title=request.POST.get('title'))
                request.session['user_info']['blog__nid'] = blog.nid
                request.session['user_info']['blog__site'] = blog.site

            data.save()
            request.session['user_info']['nickname'] = request.POST.get('nickname')
        return render(request, 'backend_base_info.html', {'obj': obj})


@check_login
def upload_avatar(request):
    ret = {'status': False, 'data': None, 'message': None}
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar_img')
        print(file_obj)
        if file_obj:
            file_name = str(uuid.uuid4())
            file_path = os.path.join('static/imgs/avatar', file_name)
            f = open(file_path, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            ret['status'] = True
            ret['data'] = file_path
            obj = models.UserInfo.objects.filter(nid=request.session.get('user_info').get('nid')).first()
            obj.avatar = '/' + file_path
            obj.save()
            request.session['user_info']['avatar'] = '/' + file_path
    return HttpResponse(json.dumps(ret))

def get_dic(request,Model,Url,blog_id,**kwargs):
    data_count = Model.objects.filter(blog_id=blog_id).count()
    page = Pagination(request.GET.get('p', 1), data_count)
    obj = Model.objects.filter(blog_id=blog_id).all()[page.start:page.end]
    page_str = page.page_str(Url)
    kwargs['p'] = page.current_page
    return {'obj': obj, 'cate_dict': kwargs, 'page_str': page_str}

@check_login
def tag(request,*args,**kwargs):
    blog_id = request.session.get('user_info').get('blog__nid')
    """
    博主个人标签管理
    :param request:
    :return:
    article, article2tag, blog, blog_id, nid, title
    """
    dic={}
    if request.method == 'GET':
        dic = get_dic(request, models.Tag, 'tag.html', blog_id, **kwargs)
        return render(request, 'backend_tag.html', dic)
    elif request.method == 'POST':
        # request.POST.get('func')
        # tag增【0】删【1】改【2】
        func = request.POST.get('func')
        if func == '0':
            # 增加
            try:
                models.Tag.objects.create(title=request.POST.get('title'),blog_id=blog_id)
                dic = get_dic(request, models.Tag, 'tag.html', blog_id, **kwargs)
            except:
                dic['err']='请先填写个人信息'
            return render(request, 'backend_tag.html', dic)
        elif func == '1':
            # 删除
            nid = request.POST.get('nid')
            try:
                assert models.Tag.objects.filter(nid=nid).delete()[0]
                ret = 'ok'
            except Exception as e:
                ret = 'err'
            return HttpResponse(ret)
        elif func == '2':
            # 修改
            print(request.POST)
            nid = request.POST.get('nid')
            title = request.POST.get('title')
            models.Tag.objects.filter(nid=nid).update(title=title)
            return HttpResponse('ok')
        else:
            return Http404


@check_login
def category(request,*args,**kwargs):
    """
    博主个人分类管理
    :param request:
    :return:
    """

    blog_id = request.session.get('user_info').get('blog__nid')
    dic={}
    if request.method == 'GET':
        dic = get_dic(request, models.Category, 'category.html', blog_id, **kwargs)
        return render(request, 'backend_category.html', dic)
    elif request.method == 'POST':
        # request.POST.get('func')
        # tag增【0】删【1】改【2】
        func = request.POST.get('func')
        if func == '0':
            # 增加
            try:
                 models.Category.objects.create(title=request.POST.get('title'),
                                           blog_id=blog_id)
                 dic =get_dic(request, models.Category, 'category.html', blog_id, **kwargs)
            except:
                dic['err']='请先填写个人信息'
            return render(request, 'backend_category.html', dic)
        elif func == '1':
            # 删除
            nid = request.POST.get('nid')
            try:
                assert models.Category.objects.filter(nid=nid).delete()[0]
                ret = 'ok'
            except Exception as e:
                ret = 'err'
            return HttpResponse(ret)
        elif func == '2':
            # 修改
            print(request.POST)
            nid = request.POST.get('nid')
            title = request.POST.get('title')
            models.Category.objects.filter(nid=nid).update(title=title)
            return HttpResponse('ok')
        else:
            return Http404


@check_login
def article(request, *args, **kwargs):
    """
    博主个人文章管理
    :param request:
    :return:
    """
    blog_id = request.session['user_info']['blog__nid']
    condition = {}
    for k, v in kwargs.items():
        if v == '0':
            pass
        else:
            condition[k] = v
    condition['blog_id'] = blog_id
    data_count = models.Article.objects.filter(**condition).count()
    page = Pagination(request.GET.get('p', 1), data_count)
    result = models.Article.objects.filter(**condition).order_by('-nid').only('nid', 'title','blog').select_related('blog')[page.start:page.end]
    page_str = page.page_str(reverse('article', kwargs=kwargs))
    category_list = models.Category.objects.filter(blog_id=blog_id).values('nid', 'title')
    type_list = map(lambda item: {'nid': item[0], 'title': item[1]}, models.Article.type_choices)
    kwargs['p'] = page.current_page
    ret = {'result': result,
           'page_str': page_str,
           'category_list': category_list,
           'type_list': type_list,
           'arg_dict': kwargs,
           'data_count': data_count
           }
    print(result,'1')
    return render(request,
                  'backend_article.html', ret)


@check_login
def add_article(request):
    """
    添加文章
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = ArticleForm(request=request)
        return render(request, 'backend_add_article.html', {'form': form})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():

            with transaction.atomic():
                tags = form.cleaned_data.pop('tags')
                content = form.cleaned_data.pop('content')
                print(content)
                content = XSSFilter().process(content)
                form.cleaned_data['blog_id'] = request.session['user_info']['blog__nid']
                print(form.cleaned_data)
                obj = models.Article.objects.create(**form.cleaned_data)
                models.ArticleDetail.objects.create(content=content, article=obj)
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            print('ok')
            return redirect('/backend/article-0-0.html')
        else:
            print('err')
            return render(request, 'backend_add_article.html', {'form': form})
    else:
        return redirect('/')


@check_login
def edit_article(request, nid):
    """
    编辑文章
    :param request:
    :return:
    """
    blog_id = request.session['user_info']['blog__nid']
    if request.method == 'GET':
        obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
        if not obj:
            return render(request, 'backend_no_article.html')
        tags = obj.tags.values_list('nid')
        if tags:
            tags = list(zip(*tags))[0]
        init_dict = {
            'nid': obj.nid,
            'title': obj.title,
            'summary': obj.summary,
            'category_id': obj.category_id,
            'article_type_id': obj.article_type_id,
            'content': obj.articledetail.content,
            'tags': tags
        }
        form = ArticleForm(request=request, data=init_dict)
        return render(request, 'backend_edit_article.html', {'form': form, 'nid': nid})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
            if not obj:
                return render(request, 'backend_no_article.html')
            with transaction.atomic():
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                tags = form.cleaned_data.pop('tags')
                models.Article.objects.filter(nid=obj.nid).update(**form.cleaned_data)
                models.ArticleDetail.objects.filter(article=obj).update(content=content)
                models.Article2Tag.objects.filter(article=obj).delete()
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect('/backend/article-0-0.html')
        else:
            print(form.errors)
            return render(request, 'backend_edit_article.html', {'form': form, 'nid': nid})
@check_login
def delete_article(request, nid):
    blog_id = request.session['user_info']['blog__nid']
    if request.method == 'GET':
        models.Article.objects.filter(nid=nid, blog_id=blog_id).delete()
    return redirect('/backend/article-0-0.html')
