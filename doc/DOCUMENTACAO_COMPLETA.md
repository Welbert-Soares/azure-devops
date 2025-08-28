# 📚 Documentação - Sistema de Automação Azure DevOps

## 🎯 Visão Geral

Este sistema automatiza a criação de work items no Azure DevOps baseado em tickets do sistema Fusion, usando Apache Airflow para orquestração e Python para integração com APIs.

## 📋 Índice

1. [Como Funciona o Sistema](#como-funciona)
2. [Arquitetura do Projeto](#arquitetura)
3. [Componentes Principais](#componentes)
4. [Configuração e Uso](#configuracao)
5. [Fluxo de Execução](#fluxo)
6. [Resolução de Problemas](#problemas)
7. [Desenvolvimento](#desenvolvimento)

---

## 🔄 Como Funciona o Sistema {#como-funciona}

### O Problema que Resolve

**Antes:** Tickets criados no sistema Fusion precisavam ser manualmente transferidos para o Azure DevOps como work items.

**Agora:** O sistema automaticamente:
1. 🔍 Busca tickets pendentes no Fusion (SQL Server)
2. ✅ Verifica se já existem cards no Azure DevOps
3. 🎯 Cria work items apenas para tickets novos
4. 📧 Envia notificação com resultados

### Fluxo Simplificado

```
📊 Fusion (SQL)  →  🔄 Airflow  →  📋 Azure DevOps
    Tickets           Processa      Work Items
```

---

## 🏗️ Arquitetura do Projeto {#arquitetura}

### Estrutura de Pastas

```
📁 azure-devops/
├── 🐳 docker-compose.yml        # Ambiente Airflow
├── 📋 dags/                     # DAGs do Airflow
│   ├── __init__.py              # Config Python path
│   └── azure_devops_production_dag.py  # DAG principal
├── 🔧 src/azure_devops_integration/    # Código de produção
│   ├── __init__.py              # Exports do pacote
│   ├── client.py                # Cliente Azure DevOps
│   └── config.py                # Configurações
├── 🧪 test_with_mocks.py        # Testes com dados falsos
├── 🔐 .env                      # Credenciais (seguro)
├── 📚 doc/                      # Documentação
└── 📝 requirements.txt          # Dependências Python
```

### Tecnologias Utilizadas

- **🐍 Python 3.13:** Linguagem principal
- **🌊 Apache Airflow 2.8.1:** Orquestração de workflows
- **🐳 Docker:** Ambiente isolado e reproduzível
- **🐘 PostgreSQL:** Banco do Airflow
- **☁️ Azure DevOps API 7.1:** Integração com Azure
- **📊 SQL Server:** Fonte dos dados (Fusion)

---

## 🧩 Componentes Principais {#componentes}

### 1. 📋 DAG Principal (`azure_devops_production_dag.py`)

**O que faz:** Orquestra todo o processo de automação

**Tasks (etapas):**
1. **`get_pending_tickets`** - Busca tickets no Fusion
2. **`check_existing_cards`** - Verifica duplicatas 
3. **`create_azure_devops_cards`** - Cria work items
4. **`send_notification`** - Envia notificação

**Exemplo de execução:**
```python
# O DAG roda automaticamente a cada 6 horas
# Ou pode ser executado manualmente no Airflow UI
```

### 2. 🔧 Cliente Azure DevOps (`client.py`)

**O que faz:** Gerencia toda comunicação com Azure DevOps

**Principais métodos:**
```python
# Testa se consegue conectar
client.test_connection()

# Cria um work item individual  
client.create_work_item_from_ticket(ticket_data)

# Cria múltiplos work items
client.create_work_items_batch(tickets_list)

# Valida dados antes de criar
client.validate_ticket(ticket_data)
```

### 3. ⚙️ Configurações (`config.py`)

**O que faz:** Define mapeamentos e configurações

**Mapeamentos importantes:**
```python
# Categoria → Tipo de Work Item
'Desenvolvimento' → 'Product backlog item'
'Bug' → 'Bug'
'Feature' → 'User Story'

# Prioridade → Número
'Crítica' → 1
'Alta' → 2  
'Normal' → 3
'Baixa' → 4
```

---

## ⚙️ Configuração e Uso {#configuracao}

### Pré-requisitos

1. **Docker Desktop** instalado
2. **Credenciais Azure DevOps:**
   - Organização (ex: `welbertsoares`)
   - Projeto (ex: `cards-kanban-welbert-teste`)
   - Personal Access Token (PAT)

### Primeira Execução

1. **Inicie o ambiente:**
```bash
docker-compose up -d
```

2. **Configure credenciais:**
```bash
# As credenciais já estão no arquivo .env
# Elas foram configuradas automaticamente no Airflow
```

3. **Acesse o Airflow:**
- URL: http://localhost:8080
- Login: admin / admin

4. **Ative o DAG:**
- Encontre `azure_devops_card_creation`
- Clique no toggle para ativar

### Execução Manual

**Via Airflow UI:**
1. Vá para http://localhost:8080
2. Clique em `azure_devops_card_creation`
3. Clique em "Trigger DAG"

**Via comando:**
```bash
docker-compose exec airflow-scheduler airflow dags trigger azure_devops_card_creation
```

### Monitoramento

**Logs em tempo real:**
```bash
docker-compose logs -f airflow-scheduler
```

**Status das execuções:**
- Acesse o Airflow UI
- Vá em "DAGs" → "azure_devops_card_creation"
- Veja histórico de execuções

---

## 🔄 Fluxo de Execução Detalhado {#fluxo}

### Etapa 1: Buscar Tickets (`get_pending_tickets`)

**O que acontece:**
```python
# 1. Conecta no SQL Server do Fusion
# 2. Executa query para buscar tickets pendentes
# 3. Filtra apenas tickets não processados
# 4. Passa dados para próxima etapa
```

**Atualmente:** Usa dados mockados (teste)
**Em produção:** Conectará ao SQL Server real

### Etapa 2: Verificar Existentes (`check_existing_cards`)

**O que acontece:**
```python
# 1. Recebe lista de tickets da etapa anterior
# 2. Para cada ticket, verifica se já existe work item
# 3. Filtra apenas tickets realmente novos
# 4. Testa conexão com Azure DevOps
```

### Etapa 3: Criar Cards (`create_azure_devops_cards`)

**O que acontece:**
```python
# 1. Recebe tickets novos da etapa anterior
# 2. Para cada ticket:
#    - Valida dados obrigatórios
#    - Mapeia categoria → tipo de work item
#    - Define prioridade e estado inicial
#    - Cria work item via API
# 3. Coleta resultados (sucessos e falhas)
```

### Etapa 4: Notificar (`send_notification`)

**O que acontece:**
```python
# 1. Coleta resultados das etapas anteriores
# 2. Monta relatório com estatísticas
# 3. Envia notificação (atualmente apenas log)
# 4. Em produção: enviará email/webhook
```

---

## 🔧 Resolução de Problemas {#problemas}

### Problema: DAG não aparece no Airflow

**Solução:**
```bash
# Verificar erros de importação
docker-compose exec airflow-scheduler airflow dags list-import-errors

# Se houver erros, verificar logs
docker-compose logs airflow-scheduler
```

### Problema: Erro de conexão Azure DevOps

**Verificações:**
1. **Token válido:** Verifique se o PAT não expirou
2. **Permissões:** Token precisa de permissão para Work Items
3. **Organização/Projeto:** Nomes devem estar corretos

**Teste manual:**
```bash
docker-compose exec airflow-scheduler python -c "
import sys
sys.path.insert(0, '/opt/airflow/src')
from azure_devops_integration.client import create_azure_devops_client
from airflow.models import Variable

org = Variable.get('azure_devops_organization')
project = Variable.get('azure_devops_project')  
pat = Variable.get('azure_devops_pat')

client = create_azure_devops_client(org, project, pat)
print('Conexão:', 'OK' if client.test_connection() else 'ERRO')
"
```

### Problema: Tasks falhando

**Investigação:**
1. **Ver logs específicos:** No Airflow UI, clique na task que falhou
2. **Verificar dados:** Confirme se os dados estão no formato esperado
3. **Testar isoladamente:** Use `test_with_mocks.py` para testar componentes

### Problema: Credenciais perdidas

**Solução:**
```bash
# Restaurar do arquivo .env
source .env

# Reconfigurar no Airflow
docker-compose exec airflow-scheduler airflow variables set azure_devops_organization "sua-org"
docker-compose exec airflow-scheduler airflow variables set azure_devops_project "seu-projeto"
docker-compose exec airflow-scheduler airflow variables set azure_devops_pat "seu-token"
```

---

## 💻 Desenvolvimento {#desenvolvimento}

### Testando Localmente

**Usar dados mockados:**
```bash
python test_with_mocks.py
```

**Testar apenas o cliente:**
```python
from src.azure_devops_integration.client import create_azure_devops_client

client = create_azure_devops_client("org", "projeto", "token")
print(client.test_connection())
```

### Adicionando Novas Funcionalidades

1. **Modificar configurações:** Edite `src/azure_devops_integration/config.py`
2. **Adicionar métodos:** Edite `src/azure_devops_integration/client.py`
3. **Modificar workflow:** Edite `dags/azure_devops_production_dag.py`
4. **Testar:** Use `test_with_mocks.py`

### Estrutura de um Ticket

```python
ticket = {
    'id': 'GITI.123456/2025',           # Obrigatório
    'titulo': 'Título do chamado',       # Obrigatório  
    'descricao': 'Descrição detalhada',  # Opcional
    'categoria': 'Desenvolvimento',      # Mapeia para tipo
    'prioridade': 'Alta',               # Mapeia para número
    'solicitante': 'Nome da Pessoa',    # Informativo
    'status': 'Pendente'                # Informativo
}
```

### Logs Importantes

**Cliente inicializando:**
```
Cliente inicializado para welbertsoares/cards-kanban-welbert-teste
```

**Conexão estabelecida:**
```
Conexão estabelecida! Projetos encontrados: 2
```

**Work item criado:**
```
Work item criado: ID 51
URL: https://dev.azure.com/.../_workitems/edit/51
```

---

## 📊 Métricas e Monitoramento

### Como Acompanhar Performance

**No Airflow UI:**
- Tempo de execução de cada task
- Taxa de sucesso/falha
- Histórico de execuções

**Logs importantes:**
- Quantos tickets foram processados
- Quantos work items foram criados
- Quais falharam e por quê

### Configurações de Execução

**Agendamento atual:** A cada 6 horas
**Timeout por task:** 30 segundos
**Tentativas em caso de falha:** 2
**Delay entre tentativas:** 5 minutos

---

## 🚀 Próximos Passos

### Para Produção Completa:

1. **Conectar SQL Server real:**
   - Configurar string de conexão
   - Implementar queries específicas do Fusion
   - Adicionar tratamento de erros de BD

2. **Melhorar notificações:**
   - Configurar envio de email
   - Implementar webhooks
   - Dashboard de métricas

3. **Otimizações:**
   - Cache de verificações
   - Processamento em paralelo
   - Retry inteligente

---

## 📞 Suporte

**Para dúvidas:**
1. Consulte esta documentação
2. Verifique logs no Airflow UI
3. Teste com `test_with_mocks.py`
4. Verifique o arquivo `CREDENTIALS_GUIDE.md`

**Arquivos importantes:**
- `.env` - Backup das credenciais
- `docker-compose.yml` - Configuração do ambiente
- `logs/` - Logs históricos do Airflow
