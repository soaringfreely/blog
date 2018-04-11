#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from django import forms
from django.forms import fields
from django.forms import widgets
from repository import models


class UserInfoForm(forms.Form):
    nickname = fields.CharField(
        widget=widgets.TextInput(attrs={"class": "form-control", "id": "nickname"})
    )
    site = fields.CharField(
        widget=widgets.TextInput(attrs={"class": "form-control",
                                        "id": "blogUrl",
                                        'placeholder': "如：wupeiqi,则个人博客为http://www.xxx.com/wupeiqi.html"})
    )
    # theme = fields.ChoiceField(
    #     widget=widgets.ChoiceWidget(attrs={"class": "form-control",
    #                                        "id": "blogTheme"},
    #                                 )
    # )
    theme = fields.ChoiceField(
        choices=models.Blog.type_choices,
        widget=widgets.Select(attrs={"class": "form-control", "id": "blogTheme"},)
    )
    title = fields.CharField(
        max_length=256,
        widget=widgets.Textarea(attrs={"class": "form-control", "id": "blogTitle"})
                             )
