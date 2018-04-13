from django import template


register = template.Library()

@register.simple_tag
def published(article_obj):
    count_a=article_obj.filter(status='published').count()
    return count_a