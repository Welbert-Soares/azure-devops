"""
Configuração do Python path para DAGs do Airflow.
Adiciona o diretório src ao sys.path para importar módulos de produção.
"""

import sys
import os

# Adiciona o diretório src ao Python path
src_path = '/opt/airflow/src'
if src_path not in sys.path:
    sys.path.insert(0, src_path)
