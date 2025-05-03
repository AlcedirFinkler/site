from rest_framework import serializers
from .models import Tenant, PlanoAssinatura

class PlanoAssinaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanoAssinatura
        fields = ['id', 'nome', 'descricao', 'preco', 'nivel', 'recursos']

class TenantSerializer(serializers.ModelSerializer):
    plano = PlanoAssinaturaSerializer(read_only=True)
    
    class Meta:
        model = Tenant
        fields = ['id', 'nome', 'slug', 'empresa', 'email', 'telefone', 'cpf_cnpj', 'plano', 'status_pagamento', 'data_vencimento', 'ativo']