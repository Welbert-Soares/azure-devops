# 🚀 Tutorial Prático - Como Usar o Sistema

## 🎯 Objetivo
Este tutorial te ensina a usar o sistema de automação Azure DevOps no dia a dia, desde ligar até monitorar.

---

## 📋 Checklist Inicial

Antes de começar, verifique se tem:
- [ ] Docker Desktop instalado e rodando
- [ ] Credenciais do Azure DevOps (organização, projeto, token)
- [ ] Acesso à pasta do projeto

---

## 🔧 Passo 1: Ligando o Sistema

### 1.1 Abrir Terminal
```bash
# Navegue até a pasta do projeto
cd C:\Users\welbert\Documents\github\azure-devops
```

### 1.2 Iniciar Containers
```bash
# Liga todo o sistema (demora ~2 minutos na primeira vez)
docker-compose up -d

# Verificar se subiu tudo
docker-compose ps
```

**Resultado esperado:**
```
✅ azure-devops-airflow-scheduler-1   Up 
✅ azure-devops-airflow-webserver-1   Up
✅ azure-devops-postgres-1            Up (healthy)
```

### 1.3 Aguardar Inicialização
```bash
# Aguarde até ver esta mensagem nos logs:
docker-compose logs airflow-webserver | Select-String "Airflow is ready"
```

---

## 🌐 Passo 2: Acessando o Airflow

### 2.1 Abrir Navegador
- URL: http://localhost:8080
- Login: `admin`
- Senha: `admin`

### 2.2 Encontrar seu DAG
1. Na tela inicial, procure por `azure_devops_card_creation`
2. Se não aparecer, clique no botão 🔄 "Refresh"

### 2.3 Verificar Status
**DAG aparece mas está pausado (❚❚):**
- ✅ Normal - DAG instalado corretamente

**DAG não aparece:**
- ❌ Problema - Vá para [Resolução de Problemas](#problemas)

---

## ⚙️ Passo 3: Configurando Credenciais

### 3.1 Verificar Variáveis Existentes
```bash
docker-compose exec airflow-scheduler airflow variables list
```

**Deve mostrar:**
- `azure_devops_organization`
- `azure_devops_project`  
- `azure_devops_pat`
- `area_path`

### 3.2 Se Precisar Reconfigurar
```bash
# Substitua pelos seus valores reais
docker-compose exec airflow-scheduler airflow variables set azure_devops_organization "sua-organizacao"
docker-compose exec airflow-scheduler airflow variables set azure_devops_project "seu-projeto"
docker-compose exec airflow-scheduler airflow variables set azure_devops_pat "seu-token"
```

### 3.3 Testar Conexão
```bash
docker-compose exec airflow-scheduler python -c "
import sys
sys.path.insert(0, '/opt/airflow/src')
from azure_devops_integration.client import create_azure_devops_client
from airflow.models import Variable

org = Variable.get('azure_devops_organization')
project = Variable.get('azure_devops_project')  
pat = Variable.get('azure_devops_pat')

print('Testando conexão...')
client = create_azure_devops_client(org, project, pat)
if client.test_connection():
    print('✅ SUCESSO: Conexão funcionando!')
else:
    print('❌ ERRO: Problema na conexão')
"
```

---

## 🚀 Passo 4: Primeira Execução

### 4.1 Ativar o DAG (Via UI)
1. Acesse http://localhost:8080
2. Encontre `azure_devops_card_creation`
3. Clique no toggle ❚❚ para ativá-lo ▶️

### 4.2 Executar Manualmente
1. Clique no nome do DAG `azure_devops_card_creation`
2. No canto direito, clique em "Trigger DAG" ▶️
3. Confirme clicando "Trigger"

### 4.3 Acompanhar Execução
1. Volte para a tela inicial
2. Você verá um círculo colorido aparecendo:
   - 🟡 **Amarelo:** Rodando
   - 🟢 **Verde:** Sucesso  
   - 🔴 **Vermelho:** Erro

---

## 👀 Passo 5: Monitoramento

### 5.1 Ver Detalhes da Execução
1. Clique no círculo colorido (execução)
2. Você verá as 4 tarefas:
   - `get_pending_tickets`
   - `check_existing_cards`  
   - `create_azure_devops_cards`
   - `send_notification`

### 5.2 Ver Logs de uma Tarefa
1. Clique numa tarefa específica
2. Clique em "Logs"
3. Veja o que aconteceu em detalhes

### 5.3 Monitorar via Terminal
```bash
# Ver logs em tempo real
docker-compose logs -f airflow-scheduler

# Filtrar apenas logs do seu DAG
docker-compose logs airflow-scheduler | Select-String "azure_devops"
```

---

## 🧪 Passo 6: Teste com Dados Reais

### 6.1 Verificar Dados Mockados
O sistema atualmente usa dados de teste. Para ver:
```bash
# Execute o teste local
python test_with_mocks.py
```

### 6.2 Criar um Work Item de Teste
```bash
docker-compose exec airflow-scheduler python -c "
import sys
sys.path.insert(0, '/opt/airflow/src')
from azure_devops_integration.client import create_azure_devops_client
from airflow.models import Variable
import time

org = Variable.get('azure_devops_organization')
project = Variable.get('azure_devops_project')  
pat = Variable.get('azure_devops_pat')

client = create_azure_devops_client(org, project, pat)

# Ticket de teste
ticket = {
    'id': f'TESTE-{int(time.time())}',
    'titulo': 'Card criado via tutorial',
    'descricao': 'Este card foi criado seguindo o tutorial',
    'categoria': 'Desenvolvimento',
    'prioridade': 'Normal',
    'solicitante': 'Tutorial Automatico'
}

print('Criando work item de teste...')
work_item_id = client.create_work_item_from_ticket(ticket)

if work_item_id:
    print(f'✅ Work item criado: {work_item_id}')
    print(f'🔗 URL: https://dev.azure.com/{org}/{project}/_workitems/edit/{work_item_id}')
else:
    print('❌ Erro ao criar work item')
"
```

### 6.3 Verificar no Azure DevOps
1. Acesse: https://dev.azure.com/sua-organizacao/seu-projeto
2. Vá em "Boards" → "Work items"
3. Procure pelo work item recém-criado

---

## 📅 Passo 7: Configurar Automação

### 7.1 Configurar Horários
O DAG roda automaticamente a cada 6 horas. Para mudar:

1. Edite o arquivo `dags/azure_devops_production_dag.py`
2. Encontre a linha:
```python
schedule_interval=AIRFLOW_CONFIG['schedule_interval']  # '0 */6 * * *'
```
3. Altere para sua preferência:
```python
schedule_interval='0 */2 * * *'    # A cada 2 horas
schedule_interval='0 9 * * *'      # Todo dia às 9h
schedule_interval='0 9 * * 1-5'    # Dias úteis às 9h
```

### 7.2 Configurar Notificações
Por enquanto, apenas logs. Para configurar email:
1. Edite `dags/azure_devops_production_dag.py`
2. Na função `send_notification()`, descomente:
```python
# TODO: Implementar envio real de notificação
# if notification_webhook:
#     send_webhook_notification(notification_webhook, message)
```

---

## 🔧 Resolução de Problemas {#problemas}

### Problema: Docker não inicia
```bash
# Verificar se Docker Desktop está rodando
docker --version

# Se não funcionar, reinicie Docker Desktop
```

### Problema: DAG não aparece
```bash
# Verificar erros de importação
docker-compose exec airflow-scheduler airflow dags list-import-errors

# Se houver erros, verificar sintaxe do código
```

### Problema: Token inválido
```bash
# Testar token manualmente
curl -u :SEU_TOKEN https://dev.azure.com/SUA_ORG/_apis/projects?api-version=7.1

# Se retornar 401, token está inválido
# Gere novo token em: https://dev.azure.com/SUA_ORG/_usersSettings/tokens
```

### Problema: Execução trava
```bash
# Ver o que está acontecendo
docker-compose logs airflow-scheduler | Select-Object -Last 50

# Reiniciar se necessário
docker-compose restart airflow-scheduler
```

---

## 📊 Comandos Úteis do Dia a Dia

### Gerenciamento do Sistema
```bash
# Ligar sistema
docker-compose up -d

# Desligar sistema  
docker-compose down

# Reiniciar apenas um serviço
docker-compose restart airflow-scheduler

# Ver status
docker-compose ps

# Ver logs recentes
docker-compose logs --tail 50 airflow-scheduler
```

### Airflow
```bash
# Listar DAGs
docker-compose exec airflow-scheduler airflow dags list

# Pausar/despausar DAG
docker-compose exec airflow-scheduler airflow dags pause azure_devops_card_creation
docker-compose exec airflow-scheduler airflow dags unpause azure_devops_card_creation

# Executar manualmente
docker-compose exec airflow-scheduler airflow dags trigger azure_devops_card_creation

# Ver variáveis
docker-compose exec airflow-scheduler airflow variables list
```

### Testes Rápidos
```bash
# Teste conexão Azure DevOps
docker-compose exec airflow-scheduler python -c "
import sys; sys.path.insert(0, '/opt/airflow/src')
from azure_devops_integration.client import create_azure_devops_client
from airflow.models import Variable
client = create_azure_devops_client(
    Variable.get('azure_devops_organization'),
    Variable.get('azure_devops_project'),
    Variable.get('azure_devops_pat')
)
print('Conexão:', 'OK' if client.test_connection() else 'ERRO')
"

# Teste local com mocks
python test_with_mocks.py
```

---

## 🎯 Checklist de Sucesso

Após seguir este tutorial, você deve conseguir:

- [ ] Ligar/desligar o sistema via Docker
- [ ] Acessar Airflow UI em http://localhost:8080
- [ ] Ver o DAG `azure_devops_card_creation` funcionando  
- [ ] Executar o DAG manualmente
- [ ] Ver logs de execução
- [ ] Criar work items de teste
- [ ] Verificar work items no Azure DevOps
- [ ] Entender onde estão as configurações

**Se todos os itens estão ✅, seu sistema está funcionando perfeitamente!**

---

## 📞 Próximos Passos

1. **Para Produção:** Substitua dados mockados por conexão SQL Server real
2. **Monitoramento:** Configure alertas de falha por email
3. **Otimização:** Ajuste horários de execução conforme necessidade
4. **Expansão:** Adicione novos tipos de work items ou campos customizados

**Seu sistema de automação está pronto para uso! 🚀**
