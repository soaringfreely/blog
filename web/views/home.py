#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from repository import models
from utils.pagination import Pagination
from django.urls import reverse
from ..forms.comment import CommentForm


def index(request, *args, **kwargs):
    """
    博客首页，展示全部博文
    :param request:
    :return:
    """
    article_type_list = models.Article.type_choices
    if kwargs:
        article_type_id = int(kwargs['article_type_id'])
        base_url = reverse('index', kwargs=kwargs)
    else:
        article_type_id = None
        base_url = '/'
    kwargs['status'] = 'published'
    data_count = article_list = models.Article.objects.filter(**kwargs).count()
    page_obj = Pagination(request.GET.get('p'),data_count)
    article_list = models.Article.objects.filter(**kwargs).order_by('-nid')[page_obj.start:page_obj.end]
    page_str = page_obj.page_str(base_url)
    top7 = models.Article.objects.order_by('comment_count')[:7]
    print(top7)
    return render(
        request,
        'index.html',
        {
            'article_list': article_list,
            'article_type_id': article_type_id,
            'article_type_list': article_type_list,
            'page_str': page_str,
            'top7': top7,
        }
    )


def home(request, site):
    """
    博主个人首页
    :param request:
    :param site: 博主的网站后缀如：http://xxx.com/wupeiqi.html
    :return:
    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    if not blog:
        return redirect('/')
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    # date_format(create_time,"%Y-%m")
    date_list = models.Article.objects.raw(
        #'select nid, count(nid) as num,date_format("%Y-%m",create_time) as ctime from repository_article group by strftime("%Y-%m",create_time)')
        'select nid, count(nid) as num,date_format(pub_date,"%%Y-%%m") as ctime from repository_article group by date_format(pub_date,"%%Y-%%m")')

    for item in date_list:
        print(item.nid,item.num,item.ctime)
    article_list = models.Article.objects.filter(blog=blog,status='published').order_by('-nid').all()

    return render(
        request,
        'home.html',
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list
        }
    )


def filter(request, site, condition, val):
    """
    分类显示
    :param request:
    :param site:
    :param condition:
    :param val:
    :return:
    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    if not blog:
        return redirect('/')
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    date_list = models.Article.objects.raw(
        #'select nid, count(nid) as num,strftime("%Y-%m",create_time) as ctime from repository_article group by strftime("%Y-%m",create_time)')
        'select nid, count(nid) as num,date_format(pub_date,"%%Y-%%m") as ctime from repository_article group by date_format(pub_date,"%%Y-%%m")')

    template_name = "home_summary_list.html"
    if condition == 'tag':
        template_name = "home_title_list.html"
        article_list = models.Article.objects.filter(tags=val, blog=blog,status='published').all()
    elif condition == 'category':
        article_list = models.Article.objects.filter(category_id=val, blog=blog,status='published').all()
    elif condition == 'date':
        article_list = models.Article.objects.filter(blog=blog,status='published').extra(
        where=['date_format(pub_date,"%%Y-%%m")=%s'], params=[val, ]).all()

        #article_list = models.Article.objects.filter(blog=blog).extra(
        #    where=['strftime("%%Y-%%m",create_time)=%s'], params=[val, ]).all()
        # select * from article where strftime("%Y-%m",create_time)=2017-02
    else:
        article_list = []

    return render(
        request,
        template_name,
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list
        }
    )


def detail(request, site, nid):
    """
    博文详细页
    :param request:
    :param site:
    :param nid:
    :return:
    
    """
    if request.method == "GET":
        blog = models.Blog.objects.filter(site=site).select_related('user').first()
        tag_list = models.Tag.objects.filter(blog=blog)
        category_list = models.Category.objects.filter(blog=blog)
        date_list = models.Article.objects.raw(
            'select nid, count(nid) as num,date_format(pub_date,"%%Y-%%m") as ctime from repository_article group by date_format(pub_date,"%%Y-%%m")')

        article = models.Article.objects.filter(blog=blog, nid=nid, status='published').select_related('category', 'articledetail').first()
        comment_list = models.Comment.objects.filter(article=article).select_related('reply').all()

        try:
            user_id = request.session.get('user_info').get('nid')
        except:
            user_id = ''
        return render(
            request,
            'home_detail.html',
            {
                'blog': blog,
                'article': article,
                'comment_list': comment_list,
                'tag_list': tag_list,
                'category_list': category_list,
                'date_list': date_list,
                'article_id': nid,
                'user_id': user_id,
            }

        )
    elif request.method == 'POST':
        data = {}
        # print(request.POST)
        data['content'] = request.POST.get('content')
        data['article_id'] = request.POST.get('article')
        try:
            user_id = request.session.get('user_info').get('nid')
            data['user_id'] = user_id
        except:
            return HttpResponse('nologin')
        if request.POST.get('reply'):
            data['reply_id'] = request.POST.get('reply')
        # print(data)
        # print(data)
        from django.db.models import F
        # models.Tb1.objects.update(num=F('num')+1)
        models.Comment.objects.create(**data)
        # sql = 'update repository_article set comment_count=2 where nid = {}'.format(request.POST.get('article'))
        # print(sql)
        models.Article.objects.filter(nid=data['article_id']).update(comment_count=F('comment_count')+1)
        return HttpResponse('ok')



def comment(request):
    '''
    文章首页点击显示评论
    :param request: 
    :return: 
    '''
    import datetime
    nid = request.POST.get('nid')
    # data = models.Comment.objects.extra(where=['article_id=%s'], params=[nid]).values()
    data = models.Comment.objects.filter(article__nid=nid).values('nid',
                                                                  'content',
                                                                  'create_time',
                                                                  'reply_id',
                                                                  'article_id',
                                                                  'user__username')
    # # print(data[2].user.username)
    # print(data)
    # data = models.Comment.objects.filter(article__nid=nid).select_related('user')
    import json
    from datetime import date
    from datetime import datetime

    class JsonCustomEncoder(json.JSONEncoder):

        def default(self, field):

            if isinstance(field, datetime):
                return field.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(field, date):
                return field.strftime('%Y-%m-%d')
            else:
                return json.JSONEncoder.default(self, field)

    dd = json.dumps(list(data), cls=JsonCustomEncoder)



    # from django.core import serializers
    # dd = serializers.serialize("json", models.Comment.objects.filter(article__nid=nid),
    #                            fields=('user', 'ussaf',))
    print(dd)
    return HttpResponse(dd)


