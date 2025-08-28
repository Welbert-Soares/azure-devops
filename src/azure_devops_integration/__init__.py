"""
Azure DevOps Integration Package
Integração para criação automática de work items no Azure DevOps via Airflow
"""

__version__ = "1.0.0"
__author__ = "Data Team"

from .client import AzureDevOpsClient, create_azure_devops_client
from .config import (
    AZURE_DEVOPS_CONFIG,
    CATEGORY_TO_WORKITEM_MAPPING,
    PRIORITY_MAPPING,
    INITIAL_STATES,
    AIRFLOW_CONFIG
)

__all__ = [
    'AzureDevOpsClient',
    'create_azure_devops_client',
    'AZURE_DEVOPS_CONFIG',
    'CATEGORY_TO_WORKITEM_MAPPING',
    'PRIORITY_MAPPING',
    'INITIAL_STATES',
    'AIRFLOW_CONFIG'
]
