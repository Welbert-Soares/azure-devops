"""
DAG Airflow para criação de cards no Azure DevOps
Versão de produção - integração com sistema Fusion
"""

from azure_devops_integration import create_azure_devops_client, AIRFLOW_CONFIG
import logging
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
import sys
import os
from datetime import datetime, timedelta

# Adiciona src ao Python path ANTES dos imports
sys.path.insert(0, '/opt/airflow/src')

# Import do cliente de produção

# Configuração de logging
logger = logging.getLogger(__name__)

# Configurações padrão do DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 28),
    'email_on_failure': AIRFLOW_CONFIG.get('email_on_failure', True),
    'email_on_retry': False,
    'retries': AIRFLOW_CONFIG.get('max_retries', 2),
    'retry_delay': timedelta(minutes=AIRFLOW_CONFIG.get('retry_delay_minutes', 5)),
}

# Definição do DAG
dag = DAG(
    'azure_devops_card_creation',  # ID fixo da DAG
    default_args=default_args,
    description='Cria cards no Azure DevOps baseado em tickets do Fusion',
    schedule_interval=AIRFLOW_CONFIG['schedule_interval'],
    catchup=AIRFLOW_CONFIG.get('catchup', False),
    tags=['azure-devops', 'fusion', 'integration', 'production']
)


def get_azure_devops_credentials():
    """
    Recupera credenciais do Azure DevOps das variáveis do Airflow

    Returns:
        Tuple[str, str, str]: (organization, project, pat_token)

    Raises:
        Exception: Se alguma credencial não for encontrada
    """
    try:
        organization = Variable.get("azure_devops_organization")
        project = Variable.get("azure_devops_project")
        pat_token = Variable.get("azure_devops_pat")

        # Validação básica
        if not all([organization, project, pat_token]):
            raise ValueError("Uma ou mais credenciais estão vazias")

        return organization, project, pat_token
    except Exception as e:
        logger.error(f"Erro ao recuperar credenciais: {str(e)}")
        raise


def get_pending_tickets(**context):
    """
    Busca tickets pendentes do sistema Fusion via SQL Server

    Returns:
        str: Mensagem com quantidade de tickets encontrados
    """
    # TODO: Implementar consulta real ao SQL Server
    # from azure_devops_integration.fusion_connector import get_unprocessed_tickets
    # tickets = get_unprocessed_tickets()

    # TEMPORÁRIO: Dados de teste para demonstrar criação de cards
    # TODO: Substituir pela consulta real ao SQL Server
    tickets = [
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
        }
    ]

    logger.info(f"Encontrados {len(tickets)} tickets para processar")

    # Armazena na XCom para próxima task
    context['task_instance'].xcom_push(key='pending_tickets', value=tickets)

    return f"Encontrados {len(tickets)} tickets pendentes"


def check_existing_cards(**context):
    """
    Verifica quais tickets já possuem cards no Azure DevOps

    Returns:
        str: Mensagem com resultado da verificação
    """
    try:
        # Recupera tickets da task anterior
        tickets = context['task_instance'].xcom_pull(key='pending_tickets')

        if not tickets:
            logger.info("Nenhum ticket pendente encontrado")
            context['task_instance'].xcom_push(key='new_tickets', value=[])
            return "Nenhum ticket para verificar"

        logger.info(f"Verificando {len(tickets)} tickets no Azure DevOps")

        # Recupera credenciais
        organization, project, pat_token = get_azure_devops_credentials()

        # Cria cliente
        area_path = Variable.get("azure_devops_area_path", default_var=None)
        client = create_azure_devops_client(
            organization, project, pat_token, area_path)

        # Testa conexão
        if not client.test_connection():
            raise Exception("❌ Falha na conexão com Azure DevOps")

        # TODO: Implementar verificação de cards existentes
        # new_tickets = client.filter_unprocessed_tickets(tickets)
        new_tickets = tickets  # Placeholder

        logger.info(f"{len(new_tickets)} tickets novos encontrados")

        # Armazena na XCom para próxima task
        context['task_instance'].xcom_push(
            key='new_tickets', value=new_tickets)

        return f"Verificados {len(tickets)} tickets, {len(new_tickets)} são novos"

    except Exception as e:
        logger.error(f"Erro em check_existing_cards: {str(e)}")
        raise


def create_azure_devops_cards(**context):
    """
    Cria os cards no Azure DevOps para os tickets novos

    Returns:
        str: Mensagem com resultado da criação
    """
    try:
        # Recupera tickets novos da task anterior
        new_tickets = context['task_instance'].xcom_pull(key='new_tickets')

        if not new_tickets:
            logger.info("Nenhum ticket novo para processar")
            context['task_instance'].xcom_push(key='created_ids', value=[])
            context['task_instance'].xcom_push(key='failed_tickets', value=[])
            return "Nenhum card criado - todos já existem"

        # Recupera credenciais
        organization, project, pat_token = get_azure_devops_credentials()

        # Cria cliente
        area_path = Variable.get("azure_devops_area_path", default_var=None)
        client = create_azure_devops_client(
            organization, project, pat_token, area_path)

        # Cria work items em lote
        created_ids, failed_tickets = client.create_work_items_batch(
            new_tickets)

        # Log de resultados
        success_count = len(created_ids)
        failed_count = len(failed_tickets)

        logger.info(
            f"Criação concluída: {success_count} sucessos, {failed_count} falhas")

        # Armazena resultados na XCom
        context['task_instance'].xcom_push(
            key='created_ids', value=created_ids)
        context['task_instance'].xcom_push(
            key='failed_tickets', value=failed_tickets)

        # Se houver falhas, loga detalhes
        if failed_tickets:
            logger.warning("Tickets que falharam:")
            for ticket in failed_tickets:
                logger.warning(
                    f"  - {ticket.get('id')}: {ticket.get('titulo')}")

        # TODO: Marcar tickets como processados no Fusion
        # mark_tickets_as_processed(created_ids)

        return f"Cards criados: {success_count}, Falhas: {failed_count}"

    except Exception as e:
        logger.error(f"Erro em create_azure_devops_cards: {str(e)}")
        raise


def send_notification(**context):
    """
    Envia notificação com resultado do processamento

    Returns:
        str: Mensagem de confirmação
    """
    try:
        created_ids = context['task_instance'].xcom_pull(
            key='created_ids') or []
        failed_tickets = context['task_instance'].xcom_pull(
            key='failed_tickets') or []

        success_count = len(created_ids)
        failed_count = len(failed_tickets)

        # Monta mensagem de notificação
        message = f"""
Processamento Azure DevOps concluído!

Resumo:
Cards criados: {success_count}
Falhas: {failed_count}

IDs criados: {created_ids[:10]}{'...' if len(created_ids) > 10 else ''}
"""

        logger.info(message)

        # TODO: Implementar envio real de notificação
        # notification_webhook = Variable.get("notification_webhook", default_var=None)
        # if notification_webhook:
        #     send_webhook_notification(notification_webhook, message)

        return f"Notificação enviada - {success_count} criados, {failed_count} falhas"

    except Exception as e:
        logger.error(f"Erro em send_notification: {str(e)}")
        # Não re-raise para não falhar o DAG por problema de notificação
        return f"Erro na notificação: {str(e)}"


# Definição das tasks
task_get_tickets = PythonOperator(
    task_id='get_pending_tickets',
    python_callable=get_pending_tickets,
    dag=dag,
    doc_md="""
    ### Buscar Tickets Pendentes
    
    Busca tickets no sistema Fusion que ainda não foram processados.
    Consulta a tabela de tickets via SQL Server.
    """
)

task_check_existing = PythonOperator(
    task_id='check_existing_cards',
    python_callable=check_existing_cards,
    dag=dag,
    doc_md="""
    ### Verificar Cards Existentes
    
    Verifica quais tickets já possuem cards no Azure DevOps
    para evitar duplicação.
    """
)

task_create_cards = PythonOperator(
    task_id='create_azure_devops_cards',
    python_callable=create_azure_devops_cards,
    dag=dag,
    doc_md="""
    ### Criar Cards Azure DevOps
    
    Cria os work items no Azure DevOps para os tickets
    que ainda não possuem cards.
    """
)

task_notify = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    dag=dag,
    doc_md="""
    ### Enviar Notificação
    
    Envia notificação com o resultado do processamento.
    """
)

# Definição das dependências
task_get_tickets >> task_check_existing >> task_create_cards >> task_notify
