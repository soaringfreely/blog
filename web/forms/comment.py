#!/usr/bin/env python 
# -*- coding: utf-8 -*-
from django import forms
from django.forms import fields
from django.forms import widgets


class CommentForm(forms.Form):
    content = fields.CharField(
        widget=widgets.TextInput(attrs={'class': 'con'})
    )

    article = fields.CharField(
        widget=widgets.TextInput(attrs={'class': 'hidden'})
    )
    user = fields.CharField(
        widget=widgets.TextInput(attrs={'class': 'hidden'})
    )
    reply = fields.CharField(
        required=False,
        widget=widgets.TextInput(attrs={'class': 'hidden'}),

    )
