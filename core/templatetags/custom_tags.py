# Crie um arquivo templatetags/custom_tags.py na pasta core

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Obtém um item de um dicionário pelo índice.
    Usado para acessar elementos específicos em um queryset.
    """
    if dictionary:
        if isinstance(key, int) and 0 <= key < len(dictionary):
            return dictionary[key]
    return None

@register.filter
def split_string(value, delimiter=','):
    """
    Divide uma string pelo delimitador especificado.
    Usado para dividir a lista de recursos dos planos.
    """
    if value:
        return value.split(delimiter)
    return []

@register.filter
def trim(value):
    """
    Remove espaços em branco no início e fim de uma string.
    """
    if value:
        return value.strip()
    return ''