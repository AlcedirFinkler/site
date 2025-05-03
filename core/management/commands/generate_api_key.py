# Criar em core/management/commands/generate_api_key.py

from django.core.management.base import BaseCommand
from rest_framework_api_key.models import APIKey
from core.models import Tenant

class Command(BaseCommand):
    help = 'Gera uma chave de API para um tenant específico'

    def add_arguments(self, parser):
        parser.add_argument('slug', type=str, help='Slug do tenant')

    def handle(self, *args, **options):
        slug = options['slug']
        
        try:
            tenant = Tenant.objects.get(slug=slug)
            # Usa o slug como prefixo para facilitar identificação
            key_name = f"tenant.{slug}"
            
            # Verifica se já existe uma chave e a revoga se necessário
            existing_keys = APIKey.objects.filter(name__startswith=f"tenant.{slug}")
            if existing_keys.exists():
                self.stdout.write(self.style.WARNING(f'Existem {existing_keys.count()} chaves antigas para este tenant. Elas serão revogadas.'))
                existing_keys.delete()
            
            # Cria uma nova chave
            api_key, key = APIKey.objects.create_key(name=key_name)
            self.stdout.write(self.style.SUCCESS(f'Chave de API criada para o tenant {tenant.nome}:'))
            self.stdout.write(self.style.SUCCESS(f'Chave: {key}'))
            self.stdout.write(self.style.WARNING('Guarde esta chave em um local seguro, pois não será possível visualizá-la novamente.'))
            
            return key
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Tenant com o slug "{slug}" não encontrado.'))
            return None