"""
Cliente Azure DevOps para integração via Airflow
Versão de produção - sem dados hardcoded ou testes
"""

import base64
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from .config import (
    AZURE_DEVOPS_CONFIG,
    CATEGORY_TO_WORKITEM_MAPPING,
    PRIORITY_MAPPING,
    INITIAL_STATES
)

# Configurar logging
logger = logging.getLogger(__name__)


class AzureDevOpsClient:
    """Cliente para integração com Azure DevOps API"""

    def __init__(self, organization: str, project: str, pat_token: str, area_path: str = None):
        """
        Inicializa o cliente Azure DevOps

        Args:
            organization: Nome da organização no Azure DevOps
            project: Nome do projeto
            pat_token: Personal Access Token
            area_path: Caminho da área (opcional)
        """
        self.organization = organization
        self.project = project
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit"

        # Configurações de timeout
        self.timeout = 30

        # Define o area path
        self.area_path = area_path or AZURE_DEVOPS_CONFIG.get(
            'default_area_path', 'Áreas meio')
        self.full_area_path = f"{project}\\{self.area_path}"

        # Codifica o PAT para autenticação
        credentials = base64.b64encode(f":{pat_token}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json-patch+json'
        }

        logger.info(f"Cliente inicializado para {organization}/{project}")

    def test_connection(self) -> bool:
        """
        Testa a conexão com a API do Azure DevOps

        Returns:
            bool: True se a conexão foi bem-sucedida
        """
        try:
            url = f"https://dev.azure.com/{self.organization}/_apis/projects?api-version={AZURE_DEVOPS_CONFIG['api_version']}"
            response = requests.get(
                url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                projects = response.json()
                logger.info(
                    f"Conexão estabelecida! Projetos encontrados: {len(projects['value'])}")
                return True
            else:
                logger.error(f"Erro na conexão: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            logger.error(f"Timeout na conexão (>{self.timeout}s)")
            return False
        except Exception as e:
            logger.error(f"Erro de conexão: {str(e)}")
            return False

    def validate_ticket(self, ticket: Dict) -> Tuple[bool, List[str]]:
        """
        Valida se um ticket tem os campos obrigatórios

        Args:
            ticket: Dicionário com dados do ticket

        Returns:
            Tuple[bool, List[str]]: (é_válido, lista_de_erros)
        """
        errors = []

        # Campos obrigatórios
        required_fields = ['id', 'titulo']

        for field in required_fields:
            if not ticket.get(field):
                errors.append(
                    f"Campo obrigatório '{field}' está vazio ou ausente")

        # Validações adicionais
        if ticket.get('titulo') and len(ticket['titulo']) > 255:
            errors.append("Título muito longo (máximo 255 caracteres)")

        if ticket.get('categoria') and ticket['categoria'] not in CATEGORY_TO_WORKITEM_MAPPING:
            errors.append(f"Categoria '{ticket['categoria']}' não mapeada")

        if ticket.get('prioridade') and ticket['prioridade'] not in PRIORITY_MAPPING:
            errors.append(f"Prioridade '{ticket['prioridade']}' não mapeada")

        is_valid = len(errors) == 0
        return is_valid, errors

    def create_work_item_from_ticket(self, ticket: Dict) -> Optional[int]:
        """
        Cria um work item baseado nos dados de um ticket do Fusion

        Args:
            ticket: Dicionário com dados do ticket

        Returns:
            Optional[int]: ID do work item criado ou None se houve erro
        """
        try:
            # Valida o ticket antes de processar
            is_valid, validation_errors = self.validate_ticket(ticket)
            if not is_valid:
                logger.error(f"Ticket inválido {ticket.get('id', 'SEM-ID')}:")
                for error in validation_errors:
                    logger.error(f"  • {error}")
                return None

            # Mapeia categoria para tipo de work item
            work_item_type = CATEGORY_TO_WORKITEM_MAPPING.get(
                ticket.get('categoria', 'Desenvolvimento'),
                "Product backlog item"
            )

            # Mapeia prioridade
            priority = PRIORITY_MAPPING.get(
                ticket.get('prioridade', 'Normal'),
                3
            )

            # Estado inicial
            initial_state = INITIAL_STATES.get(work_item_type, "Backlog")

            # Monta URL
            url = f"{self.base_url}/workitems/${work_item_type}?api-version={AZURE_DEVOPS_CONFIG['api_version']}"

            # Monta descrição enriquecida
            description = self._build_description(ticket)

            # Patch document
            patch_document = [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": f"[{ticket.get('id', 'SEM-ID')}] {ticket.get('titulo', 'Sem título')}"
                },
                {
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": description
                },
                {
                    "op": "add",
                    "path": "/fields/System.State",
                    "value": initial_state
                },
                {
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.Priority",
                    "value": priority
                },
                {
                    "op": "add",
                    "path": "/fields/System.AreaPath",
                    "value": self.full_area_path
                }
            ]

            # Adiciona campo ID Chamado Fusion se existir no tipo de work item
            if self._field_exists_in_work_item_type(work_item_type, "Custom.IDChamadoFusion"):
                patch_document.append({
                    "op": "add",
                    "path": "/fields/Custom.IDChamadoFusion",
                    "value": ticket.get('id', 'SEM-ID')
                })
                logger.info(
                    f"Campo 'ID Chamado Fusion' adicionado: {ticket.get('id')}")
            else:
                logger.warning(
                    f"Campo 'ID Chamado Fusion' não existe no tipo '{work_item_type}'")

            logger.info(
                f"Criando work item: {work_item_type} - {ticket.get('id')}")

            response = requests.post(
                url, headers=self.headers, json=patch_document, timeout=self.timeout)

            if response.status_code == 200:
                work_item = response.json()
                work_item_id = work_item['id']
                work_item_url = work_item.get('_links', {}).get(
                    'html', {}).get('href', '')

                logger.info(f"Work item criado: ID {work_item_id}")
                logger.info(f"URL: {work_item_url}")

                return work_item_id
            else:
                logger.error(
                    f"Erro ao criar work item: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            logger.error(
                f"Erro ao processar ticket {ticket.get('id')}: {str(e)}")
            return None

    def create_work_items_batch(self, tickets: List[Dict]) -> Tuple[List[int], List[Dict]]:
        """
        Cria múltiplos work items em lote

        Args:
            tickets: Lista de dicionários com dados dos tickets

        Returns:
            Tuple[List[int], List[Dict]]: (IDs_criados, tickets_falharam)
        """
        created_ids = []
        failed_tickets = []

        logger.info(f"Iniciando criação de {len(tickets)} work items...")

        for i, ticket in enumerate(tickets, 1):
            logger.info(f"Processando {i}/{len(tickets)}: {ticket.get('id')}")

            work_item_id = self.create_work_item_from_ticket(ticket)

            if work_item_id:
                created_ids.append(work_item_id)
            else:
                failed_tickets.append(ticket)

        logger.info(
            f"Concluído: {len(created_ids)} criados, {len(failed_tickets)} falharam")

        return created_ids, failed_tickets

    def _build_description(self, ticket: Dict) -> str:
        """
        Monta descrição enriquecida do work item

        Args:
            ticket: Dicionário com dados do ticket

        Returns:
            str: Descrição HTML formatada
        """
        import html

        # Escapa caracteres especiais HTML para segurança
        safe_id = html.escape(str(ticket.get('id', 'N/A')))
        safe_desc = html.escape(str(ticket.get('descricao', 'Sem descrição')))
        safe_solicitante = html.escape(str(ticket.get('solicitante', 'N/A')))
        safe_categoria = html.escape(str(ticket.get('categoria', 'N/A')))
        safe_prioridade = html.escape(str(ticket.get('prioridade', 'N/A')))
        safe_status = html.escape(str(ticket.get('status', 'N/A')))

        description = f"""
<h3>📋 Detalhes do Chamado</h3>
<p><strong>ID Original:</strong> {safe_id}</p>
<p><strong>Descrição:</strong> {safe_desc}</p>
<p><strong>Solicitante:</strong> {safe_solicitante}</p>
<p><strong>Categoria:</strong> {safe_categoria}</p>
<p><strong>Prioridade:</strong> {safe_prioridade}</p>
<p><strong>Status Original:</strong> {safe_status}</p>

<h3>🤖 Informações de Integração</h3>
<p><strong>Importado via:</strong> Airflow + Fusion Integration</p>
<p><strong>Data de Importação:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p><strong>Área de Destino:</strong> {html.escape(self.full_area_path)}</p>
"""
        return description

    def _field_exists_in_work_item_type(self, work_item_type: str, field_reference_name: str) -> bool:
        """
        Verifica se um campo específico existe em um tipo de work item

        Args:
            work_item_type: Nome do tipo de work item
            field_reference_name: Nome de referência do campo

        Returns:
            bool: True se o campo existe
        """
        try:
            url = f"{self.base_url}/workitemtypes/{work_item_type}?api-version={AZURE_DEVOPS_CONFIG['api_version']}"
            response = requests.get(
                url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                work_item_type_data = response.json()
                fields = work_item_type_data.get('fields', [])

                # Procura pelo campo específico
                for field in fields:
                    if field.get('referenceName') == field_reference_name:
                        return True

                return False
            else:
                logger.warning(
                    f"Erro ao verificar campos do tipo '{work_item_type}': {response.status_code}")
                return False

        except Exception as e:
            logger.warning(
                f"Erro ao verificar campo '{field_reference_name}': {str(e)}")
            return False


def create_azure_devops_client(organization: str, project: str, pat_token: str, area_path: str = None) -> AzureDevOpsClient:
    """
    Factory function para criar cliente Azure DevOps

    Args:
        organization: Nome da organização no Azure DevOps
        project: Nome do projeto
        pat_token: Personal Access Token
        area_path: Caminho da área (opcional)

    Returns:
        AzureDevOpsClient: Instância do cliente configurada
    """
    return AzureDevOpsClient(organization, project, pat_token, area_path)
