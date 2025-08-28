# 🔧 Guia Técnico - Entendendo o Código

## 🎯 Para que serve cada arquivo

### 📁 `src/azure_devops_integration/`

#### `client.py` - O Coração do Sistema
```python
class AzureDevOpsClient:
    # Este é o "cérebro" que fala com Azure DevOps
```

**O que faz:**
- 🔐 **Autenticação:** Usa seu token para se conectar
- 📋 **Criação:** Transforma tickets em work items
- ✅ **Validação:** Verifica se os dados estão corretos
- 🔄 **Batch:** Processa vários tickets de uma vez

**Principais métodos explicados:**

```python
def __init__(self, organization, project, pat_token):
    # Configura o cliente com suas credenciais
    # É como "fazer login" no Azure DevOps
    
def test_connection(self):
    # Testa se consegue falar com Azure DevOps
    # Retorna True se funcionou, False se deu erro
    
def create_work_item_from_ticket(self, ticket):
    # Pega um ticket do Fusion e cria um work item
    # É aqui que a "mágica" acontece
    
def validate_ticket(self, ticket):
    # Verifica se o ticket tem tudo que precisa
    # Evita criar work items com dados quebrados
```

#### `config.py` - As Regras do Jogo
```python
# Define como transformar dados do Fusion em Azure DevOps
```

**Mapeamentos importantes:**
```python
CATEGORY_TO_WORKITEM_MAPPING = {
    'Desenvolvimento': 'Product backlog item',
    'Bug': 'Bug',
    'Feature': 'User Story'
}
# Traduz: "Desenvolvimento" vira "Product backlog item"

PRIORITY_MAPPING = {
    'Crítica': 1,    # Mais urgente
    'Alta': 2,
    'Normal': 3,
    'Baixa': 4       # Menos urgente
}
# Traduz: "Crítica" vira número 1
```

#### `__init__.py` - O Cartão de Visitas
```python
# Define o que outros arquivos podem usar
from .client import AzureDevOpsClient
from .config import AZURE_DEVOPS_CONFIG
```

### 📁 `dags/`

#### `azure_devops_production_dag.py` - O Maestro
```python
# Este arquivo diz ao Airflow o que fazer e quando
```

**Estrutura do DAG:**
```python
# 1. Configurações
default_args = {
    'owner': 'data-team',        # Quem é responsável
    'retries': 2,                # Tenta 2 vezes se der erro
    'retry_delay': 5 minutos     # Espera 5min entre tentativas
}

# 2. Definição do workflow
dag = DAG(
    'azure_devops_card_creation',    # Nome do processo
    schedule_interval='0 */6 * * *'  # Roda a cada 6 horas
)

# 3. As tarefas (tasks)
task1 >> task2 >> task3 >> task4  # Ordem de execução
```

**As 4 etapas explicadas:**

```python
def get_pending_tickets():
    # 📊 ETAPA 1: Buscar dados
    # Conecta no SQL Server do Fusion
    # Pega tickets que ainda não foram processados
    # Retorna lista de tickets
    
def check_existing_cards():
    # 🔍 ETAPA 2: Verificar duplicatas  
    # Para cada ticket, verifica se já virou work item
    # Filtra apenas os novos
    # Evita criar duplicatas
    
def create_azure_devops_cards():
    # 🎯 ETAPA 3: Criar work items
    # Para cada ticket novo:
    #   - Valida os dados
    #   - Chama a API do Azure DevOps  
    #   - Cria o work item
    #   - Salva o resultado
    
def send_notification():
    # 📧 ETAPA 4: Avisar resultado
    # Conta quantos deram certo/errado
    # Manda notificação (email/webhook)
    # Registra nos logs
```

---

## 🔄 Como o Fluxo Funciona (Passo a Passo)

### Momento 1: Airflow Desperta
```
⏰ 06:00 - Airflow verifica: "É hora de rodar?"
✅ Sim! Inicia o DAG azure_devops_card_creation
```

### Momento 2: Buscar Tickets
```python
# ETAPA 1: get_pending_tickets()
📊 SQL Server (Fusion):
   SELECT * FROM tickets WHERE status = 'pendente'
   
📋 Resultado: 
   [
     {'id': 'GITI.123', 'titulo': 'Bug crítico'},
     {'id': 'GITI.124', 'titulo': 'Nova feature'}
   ]
```

### Momento 3: Verificar Duplicatas
```python
# ETAPA 2: check_existing_cards()
🔍 Para cada ticket:
   - Conecta Azure DevOps
   - Procura work item com mesmo ID
   - Se não encontrar, é "novo"
   
📊 Resultado:
   Novos: [GITI.123, GITI.124]
   Já existem: []
```

### Momento 4: Criar Work Items
```python
# ETAPA 3: create_azure_devops_cards()
🎯 Para GITI.123:
   ✅ Valida dados
   🔄 Mapeia 'Bug' → 'Bug'
   🔄 Mapeia 'Crítica' → 1
   🌐 Chama API Azure DevOps
   ✅ Work item criado: ID 52
   
🎯 Para GITI.124:
   ✅ Valida dados  
   🔄 Mapeia 'Feature' → 'User Story'
   🔄 Mapeia 'Normal' → 3
   🌐 Chama API Azure DevOps
   ✅ Work item criado: ID 53
```

### Momento 5: Notificar
```python
# ETAPA 4: send_notification()
📊 Relatório:
   - Processados: 2 tickets
   - Criados: 2 work items
   - Falharam: 0
   - IDs criados: [52, 53]
   
📧 Envia notificação de sucesso
```

---

## 🧪 Entendendo os Testes

### `test_with_mocks.py` - Laboratório de Testes
```python
# Usa dados falsos para testar sem mexer no sistema real
```

**Por que usar dados falsos?**
- ✅ Não bagunça dados reais
- ✅ Testa rapidamente  
- ✅ Não precisa de conexão SQL Server
- ✅ Simula diferentes cenários

**Exemplo de dados mockados:**
```python
MOCK_TICKETS = [
    {
        'id': 'TESTE-123',
        'titulo': 'Ticket de teste',
        'categoria': 'Desenvolvimento', 
        'prioridade': 'Normal'
    }
]
# Simula o que viria do SQL Server real
```

---

## 🔐 Entendendo as Credenciais

### Onde ficam armazenadas:

1. **`.env`** - Backup local (seguro, não vai pro Git)
```env
AZURE_DEVOPS_ORGANIZATION=welbertsoares
AZURE_DEVOPS_PROJECT=cards-kanban-welbert-teste  
AZURE_DEVOPS_PAT=sua_token_aqui
```

2. **Airflow Variables** - Usado pelo sistema
```bash
# Como ver:
docker-compose exec airflow-scheduler airflow variables list

# Como configurar:
docker-compose exec airflow-scheduler airflow variables set azure_devops_organization "valor"
```

### Como a autenticação funciona:
```python
# 1. Pega o token
pat_token = "sua_token_pessoal"

# 2. Codifica para Basic Auth (padrão Azure)
credentials = base64.b64encode(f":{pat_token}".encode()).decode()

# 3. Monta header HTTP
headers = {
    'Authorization': f'Basic {credentials}',
    'Content-Type': 'application/json-patch+json'
}

# 4. Usa em todas as chamadas da API
response = requests.post(url, headers=headers, json=data)
```

---

## 📊 Entendendo os Logs

### Tipos de Log e o que significam:

```python
# ✅ SUCESSO
"Cliente inicializado para welbertsoares/cards-kanban-welbert-teste"
→ Sistema conectou corretamente

"Conexão estabelecida! Projetos encontrados: 2"  
→ Azure DevOps respondeu e tem acesso aos projetos

"Work item criado: ID 51"
→ Ticket virou work item com sucesso

# ⚠️ AVISO  
"Campo 'ID Chamado Fusion' não existe no tipo 'Bug'"
→ Tentou usar campo customizado que não existe (normal)

# ❌ ERRO
"Erro na conexão: 401"
→ Token inválido ou expirado

"Ticket inválido GITI.123: Campo obrigatório 'titulo' está vazio"
→ Dados do ticket estão quebrados
```

### Como ler logs no Airflow:
1. Acesse http://localhost:8080
2. Clique no DAG `azure_devops_card_creation`
3. Clique numa execução (círculo colorido)
4. Clique numa task específica
5. Clique em "Logs"

---

## 🔄 Docker: O Ambiente Isolado

### Por que usar Docker?
```
🏠 Seu computador:
├── Windows + suas configurações
├── Seus programas
└── 📦 Container Docker (mundo isolado):
    ├── Ubuntu Linux
    ├── Python 3.8
    ├── Airflow 2.8.1
    ├── PostgreSQL
    └── Seu código
```

**Vantagens:**
- ✅ Não bagunça seu computador
- ✅ Funciona igual em qualquer máquina
- ✅ Fácil de ligar/desligar
- ✅ Versões fixas (não quebra)

### Comandos essenciais:
```bash
# Ligar todo o sistema
docker-compose up -d

# Ver o que está rodando  
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f airflow-scheduler

# Entrar "dentro" do container
docker-compose exec airflow-scheduler bash

# Desligar tudo
docker-compose down
```

---

## 🎯 Resumo: O que cada parte faz

| Componente | Função | Analogia |
|------------|--------|----------|
| **Docker** | Ambiente isolado | Casa onde tudo roda |
| **Airflow** | Orquestrador | Maestro da orquestra |
| **DAG** | Receita do processo | Lista de tarefas |
| **Client** | Comunicador | Tradutor que fala com Azure |
| **Config** | Regras | Dicionário de traduções |
| **Logs** | Histórico | Diário do que aconteceu |
| **Variáveis** | Credenciais | Chaves da casa |

### O Fluxo Completo:
```
📊 Fusion → 🔄 Airflow → 🧠 Client → ☁️ Azure DevOps
   Dados     Processa    Traduz     Work Items
```

**Em palavras simples:**
1. **Airflow** acorda de 6 em 6 horas
2. **Pergunta** ao Fusion: "Tem ticket novo?"  
3. **Pega** os tickets e fala pro **Client**: "Cria isso no Azure"
4. **Client** traduz cada ticket em work item
5. **Envia** via API para Azure DevOps
6. **Avisa** que terminou

Agora você entende como seu sistema funciona! 🚀
