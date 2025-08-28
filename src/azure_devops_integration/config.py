"""
Configurações para integração Azure DevOps + Airflow
"""

# Azure DevOps Configuration
AZURE_DEVOPS_CONFIG = {
    'api_version': '7.1',
    'base_url_template': 'https://dev.azure.com/{organization}/{project}/_apis/wit',
    'projects_url_template': 'https://dev.azure.com/{organization}/_apis/projects',
    'boards_url_template': 'https://dev.azure.com/{organization}/{project}/_apis/work/boards',
    'wiql_url_template': 'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql',
    'default_area_path': 'Áreas meio'  # Área padrão para work items do Fusion
}

# Work Item Type Mappings (Ambiente de Produção)
CATEGORY_TO_WORKITEM_MAPPING = {
    'Bug': "Product backlog item",           # Mapeado para PBI
    'Melhoria': "Melhoria pontual",          # Tipo específico configurado
    'Feature': "Product backlog item",       # Mapeado para PBI
    'Desenvolvimento': "Product backlog item",  # Tipo principal
    'Incidente': "Product backlog item",     # Mapeado para PBI
    'Solicitação': "Product backlog item",   # Mapeado para PBI
    'Tarefa': "Product backlog item",        # Mapeado para PBI
    'História': "Product backlog item"       # Mapeado para PBI
}

# Priority Mappings
PRIORITY_MAPPING = {
    'Baixa': 4,
    'Normal': 3,
    'Alta': 2,
    'Crítica': 1,
    'Urgente': 1
}

# Initial States for Work Item Types (Ambiente de Produção)
INITIAL_STATES = {
    "Product backlog item": "Backlog",   # Tipo principal configurado
    "Melhoria pontual": "Backlog",       # Tipo específico configurado
}

# Airflow Configuration
AIRFLOW_CONFIG = {
    'dag_id': 'azure_devops_card_creation',
    'schedule_interval': '0 */6 * * *',  # A cada 6 horas
    'max_retries': 2,
    'retry_delay_minutes': 5,
    'email_on_failure': True,
    'catchup': False
}

# SQL Server Configuration (para próximas fases)
SQL_SERVER_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'query_timeout': 30,
    'connection_timeout': 15
}

# Fusion System Configuration (para próximas fases)
FUSION_CONFIG = {
    'tickets_table': 'tickets_fusion',
    'processed_tickets_table': 'azure_devops_processed',
    'batch_size': 50,
    'max_days_lookback': 30
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': ['console', 'file']
}
