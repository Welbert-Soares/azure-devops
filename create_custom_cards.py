#!/usr/bin/env python3
"""
Script para criar cards personalizados no Azure DevOps
Edite os dados de teste abaixo e execute para criar seus próprios cards
"""
import os
from azure_devops_integration import create_azure_devops_client
import sys
sys.path.insert(0, '/opt/airflow/src')


def create_custom_cards():
    """
    Cria cards personalizados - EDITE OS DADOS ABAIXO!
    """
    # 🎯 PERSONALIZE SEUS DADOS DE TESTE AQUI:
    tickets = [
        {
            'id': 'CUSTOM.001/2025',
            'titulo': 'Implementar nova funcionalidade de relatórios',
            'description': 'Criar sistema de relatórios dinâmicos para o dashboard principal',
            'category': 'Desenvolvimento',
            'priority': 'Alta',
            'requester': 'Product Owner',
            'department': 'Produto'
        },
        {
            'id': 'CUSTOM.002/2025',
            'titulo': 'Corrigir problema de performance na API',
            'description': 'Otimizar consultas SQL que estão causando lentidão na API de usuários',
            'category': 'Bug',
            'priority': 'Crítica',
            'requester': 'Suporte Técnico',
            'department': 'TI'
        },
        {
            'id': 'CUSTOM.003/2025',
            'titulo': 'Melhorar UX do formulário de cadastro',
            'description': 'Redesenhar interface do formulário baseado no feedback dos usuários',
            'category': 'Melhoria',
            'priority': 'Média',
            'requester': 'UX Designer',
            'department': 'Design'
        }
    ]

    print(f"🎯 Criando {len(tickets)} cards personalizados...")

    try:
        # Conectar ao Azure DevOps
        pat_token = os.getenv('AZURE_DEVOPS_PAT')
        if not pat_token:
            print("❌ Token PAT não encontrado! Configure a variável AZURE_DEVOPS_PAT")
            return False

        client = create_azure_devops_client(
            'welbertsoares',
            'cards-kanban-welbert-teste',
            pat_token
        )

        # Criar cards
        created_ids, failed_tickets = client.create_work_items_batch(tickets)

        print(f"\n📊 Resultado:")
        print(f"   ✅ Cards criados: {len(created_ids)}")
        print(f"   ❌ Falhas: {len(failed_tickets)}")

        if created_ids:
            print(f"\n🎉 Cards criados com sucesso:")
            for i, ticket in enumerate(tickets):
                if i < len(created_ids):
                    print(f"   • {ticket['id']}: {ticket['titulo']}")
                    print(f"     Azure DevOps ID: {created_ids[i]}")
                    print()

        if failed_tickets:
            print(f"\n⚠️ Tickets que falharam:")
            for ticket in failed_tickets:
                print(f"   • {ticket['id']}")

        return len(created_ids) > 0

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando criação de cards personalizados...")
    success = create_custom_cards()

    if success:
        print("\n🎯 Cards criados com sucesso!")
        print("💡 Acesse o Azure DevOps para visualizar: https://dev.azure.com/welbertsoares/cards-kanban-welbert-teste")
    else:
        print("\n💥 Falhou na criação dos cards!")
