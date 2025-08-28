#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples com dados mockados para Azure DevOps Client.
Use este arquivo para testar o código enquanto não tem acesso ao SQL Server real.
"""

from azure_devops_integration.config import (
    AZURE_DEVOPS_CONFIG,
    CATEGORY_TO_WORKITEM_MAPPING,
    PRIORITY_MAPPING
)
from azure_devops_integration.client import AzureDevOpsClient
import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importa o código de produção

# DADOS MOCKADOS (simula o que viria do SQL Server)
MOCK_TICKETS = [
    {
        'id': 'GITI.123456/2025',
        'title': 'Configurar ambiente de desenvolvimento',
        'description': 'Configurar o ambiente local para desenvolvimento da aplicação',
        'category': 'Desenvolvimento',
        'priority': 'Alta',
        'requester': 'João Silva',
        'department': 'TI'
    },
    {
        'id': 'GITI.123457/2025',
        'title': 'Corrigir bug na validação de formulário',
        'description': 'O formulário não está validando campos obrigatórios corretamente',
        'category': 'Bug',
        'priority': 'Crítica',
        'requester': 'Maria Santos',
        'department': 'Qualidade'
    },
    {
        'id': 'GITI.123458/2025',
        'title': 'Implementar nova funcionalidade de relatórios',
        'description': 'Criar relatórios customizados para gestores',
        'category': 'Feature',
        'priority': 'Normal',
        'requester': 'Pedro Costa',
        'department': 'Negócios'
    }
]

# CREDENCIAIS MOCKADAS (para teste)
MOCK_CREDENTIALS = {
    'organization': 'test-organization',
    'project': 'test-project',
    'personal_access_token': 'fake-token-for-testing',
    'api_version': '7.1'
}


def test_client_creation():
    """Testa criação do cliente"""
    print("🧪 === TESTE CRIAÇÃO DO CLIENTE ===")

    try:
        client = AzureDevOpsClient(
            organization=MOCK_CREDENTIALS['organization'],
            project=MOCK_CREDENTIALS['project'],
            pat_token=MOCK_CREDENTIALS['personal_access_token']
        )
        print(f"✅ Cliente criado: {client.organization}/{client.project}")
        return client
    except Exception as e:
        print(f"❌ Erro ao criar cliente: {e}")
        return None


def test_ticket_validation(client):
    """Testa validação de tickets"""
    print("\n🧪 === TESTE VALIDAÇÃO DE TICKETS ===")

    if not client:
        print("❌ Cliente não está disponível")
        return False

    try:
        # Testa cada ticket mockado
        valid_count = 0
        for ticket in MOCK_TICKETS:
            is_valid = client.validate_ticket(ticket)
            status = "✅ Válido" if is_valid else "❌ Inválido"
            print(f"📋 {ticket['id']}: {status}")
            if is_valid:
                valid_count += 1

        print(
            f"\n📊 Resultado: {valid_count}/{len(MOCK_TICKETS)} tickets válidos")
        return valid_count > 0

    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False


def test_configuration():
    """Testa configurações"""
    print("\n🧪 === TESTE CONFIGURAÇÕES ===")

    try:
        print(f"✅ API Version: {AZURE_DEVOPS_CONFIG['api_version']}")
        print(f"✅ Categorias mapeadas: {len(CATEGORY_TO_WORKITEM_MAPPING)}")
        print(f"✅ Prioridades mapeadas: {len(PRIORITY_MAPPING)}")

        print("\n📋 Alguns mapeamentos:")
        for category, work_item_type in list(CATEGORY_TO_WORKITEM_MAPPING.items())[:3]:
            print(f"   {category} → {work_item_type}")

        return True

    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False


def simulate_sql_server_data():
    """Simula busca de dados do SQL Server"""
    print("\n🧪 === SIMULANDO DADOS DO SQL SERVER ===")

    # Em produção, aqui seria uma query real no SQL Server
    # Exemplo: SELECT id, title, description, category, priority FROM tickets WHERE status = 'pending'

    print("📊 Simulando query: SELECT * FROM tickets WHERE status = 'pending'")
    print(f"📋 Encontrados {len(MOCK_TICKETS)} tickets pendentes")

    for i, ticket in enumerate(MOCK_TICKETS, 1):
        print(f"\n📋 Ticket {i}:")
        print(f"   ID: {ticket['id']}")
        print(f"   Título: {ticket['title']}")
        print(f"   Categoria: {ticket['category']}")
        print(f"   Prioridade: {ticket['priority']}")

    return MOCK_TICKETS


def main():
    """Executa todos os testes"""
    print("🚀 TESTE COM DADOS MOCKADOS - AZURE DEVOPS INTEGRATION")
    print("=" * 60)
    print("ℹ️  Este teste usa dados falsos para simular o SQL Server")
    print("ℹ️  Em produção, os dados virão de queries reais no banco")
    print("=" * 60)

    # Testa criação do cliente
    client = test_client_creation()

    # Testa validação
    validation_ok = test_ticket_validation(client)

    # Testa configuração
    config_ok = test_configuration()

    # Simula dados do SQL Server
    sql_data = simulate_sql_server_data()

    # Resultado final
    print("\n" + "=" * 60)
    if client and validation_ok and config_ok and sql_data:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Código de produção está funcionando com dados mockados")
        print("📌 Próximo passo: conectar ao SQL Server real")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")

    return client and validation_ok and config_ok


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
