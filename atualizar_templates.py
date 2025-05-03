#!/usr/bin/env python
import os
import shutil
from pathlib import Path

# Verificar a estrutura de diretórios
def verify_and_create_dirs():
    dirs = [
        'core/templatetags',
        'templates'
    ]
    
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            print(f"Criando diretório: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)

# Criar arquivos de templatetags
def create_templatetags_files():
    init_file = 'core/templatetags/__init__.py'
    custom_tags_file = 'core/templatetags/custom_tags.py'
    
    if not os.path.exists(init_file):
        print(f"Criando arquivo: {init_file}")
        with open(init_file, 'w') as f:
            f.write("# Este arquivo é necessário para que o diretório templatetags seja reconhecido como um pacote Python.\n")
    
    print(f"Criando/atualizando arquivo: {custom_tags_file}")
    with open(custom_tags_file, 'w') as f:
        f.write("""from django import template

register = template.Library()

@register.filter
def get_item(list_obj, i):
    try:
        return list_obj[i]
    except:
        return None

@register.filter
def trim(value):
    return value.strip() if value else ""

@register.filter
def split_string(value, separator=','):
    \"\"\"
    Retorna uma lista obtida dividindo a string pelo separador.
    Uso no template: {{ valor|split_string:',' }}
    \"\"\"
    if value:
        return value.split(separator)
    return []
""")

# Atualizar templates
def update_templates():
    templates = {
        'base.html': 'templates/base.html',
        'navbar-home.html': 'templates/navbar-home.html',
        'navbar-secundario.html': 'templates/navbar-secundario.html',
        'hero.html': 'templates/hero.html',
        'login.html': 'templates/login.html',
        'cadastro_usuario.html': 'templates/cadastro_usuario.html',
        'cadastro_tenant.html': 'templates/cadastro_tenant.html',
        'tenant_sucesso.html': 'templates/tenant_sucesso.html',
        'planos.html': 'templates/planos.html',
        'precos.html': 'templates/precos.html'
    }
    
    current_dir = Path(__file__).parent
    
    for template_name, template_path in templates.items():
        source_file = current_dir / f"{template_name}"
        if os.path.exists(source_file):
            print(f"Atualizando template: {template_path}")
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            shutil.copy2(source_file, template_path)
        else:
            print(f"ATENÇÃO: Arquivo fonte não encontrado: {source_file}")

if __name__ == "__main__":
    print("Iniciando atualização dos templates...")
    verify_and_create_dirs()
    create_templatetags_files()
    update_templates()
    print("Atualização concluída!")
    print("\nPara verificar se o problema foi resolvido, reinicie o servidor Django:")
    print("python manage.py runserver")