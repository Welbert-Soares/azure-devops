# 🔍 FAQ - Perguntas Frequentes

## 🤔 Dúvidas Gerais

### Q: O que exatamente este sistema faz?
**R:** Automatiza a criação de work items no Azure DevOps baseado em tickets do sistema Fusion. Em vez de criar manualmente cada card, o sistema:
1. Pega tickets pendentes do Fusion (SQL Server)
2. Verifica se já existem no Azure DevOps  
3. Cria automaticamente os work items novos
4. Envia notificação com resultados

### Q: Por que usar Airflow? Não poderia ser um script simples?
**R:** Airflow oferece vantagens importantes:
- ✅ **Agendamento:** Roda automaticamente de 6 em 6 horas
- ✅ **Monitoramento:** Interface visual para ver execuções
- ✅ **Retry:** Tenta novamente se der erro
- ✅ **Logs:** Histórico completo de execuções
- ✅ **Escalabilidade:** Pode processar milhares de tickets

### Q: É seguro? Minhas credenciais ficam protegidas?
**R:** Sim, muito seguro:
- 🔐 Credenciais ficam em variáveis do Airflow, não no código
- 🔐 Arquivo `.env` não vai para Git (está no `.gitignore`)
- 🔐 Docker isola o ambiente
- 🔐 Comunicação HTTPS com Azure DevOps

---

## 🛠️ Problemas Técnicos

### Q: DAG não aparece no Airflow, o que fazer?
**R:** Verificações em ordem:
1. **Erros de importação:** `docker-compose exec airflow-scheduler airflow dags list-import-errors`
2. **Python path:** Verifique se `sys.path.insert(0, '/opt/airflow/src')` está no DAG
3. **Sintaxe:** Procure erros no código Python
4. **Reiniciar:** `docker-compose restart airflow-scheduler`

### Q: Erro "ModuleNotFoundError: No module named 'azure_devops_integration'"
**R:** Problema de Python path. Solução:
```python
# No início do arquivo DAG, adicione:
import sys
sys.path.insert(0, '/opt/airflow/src')
# DEPOIS importe o módulo:
from azure_devops_integration import create_azure_devops_client
```

### Q: Erro de conexão 401 no Azure DevOps
**R:** Token expirado ou inválido:
1. Gere novo token: https://dev.azure.com/SUA_ORG/_usersSettings/tokens
2. Permissões necessárias: "Work Items (Read & Write)"
3. Atualize no Airflow: 
```bash
docker-compose exec airflow-scheduler airflow variables set azure_devops_pat "NOVO_TOKEN"
```

### Q: DAG fica travado em "running" forever
**R:** Possíveis causas:
- **Timeout:** Task pode estar demorando mais que 30 segundos
- **SQL Server:** Conexão pode estar lenta/travada
- **Azure DevOps:** API pode estar indisponível
- **Solução:** Verifique logs e reinicie se necessário

---

## 🔧 Configurações e Customizações

### Q: Como mudar o horário de execução?
**R:** Edite `dags/azure_devops_production_dag.py`:
```python
# Atual: a cada 6 horas
schedule_interval='0 */6 * * *'

# Exemplos de outras configurações:
schedule_interval='0 9 * * *'      # Todo dia às 9h
schedule_interval='0 9 * * 1-5'    # Apenas dias úteis às 9h  
schedule_interval='*/30 * * * *'   # A cada 30 minutos
schedule_interval=None             # Apenas manual
```

### Q: Como adicionar novos tipos de work item?
**R:** Edite `src/azure_devops_integration/config.py`:
```python
CATEGORY_TO_WORKITEM_MAPPING = {
    'Desenvolvimento': 'Product backlog item',
    'Bug': 'Bug',
    'Melhoria': 'User Story',           # Adicione aqui
    'Documentação': 'Task',             # Adicione aqui
}
```

### Q: Como mudar a área de destino dos work items?
**R:** Configure a variável no Airflow:
```bash
docker-compose exec airflow-scheduler airflow variables set area_path "Nova\Área\Caminho"
```

### Q: Como desativar o DAG temporariamente?
**R:** Duas opções:
1. **Via UI:** http://localhost:8080 → toggle ❚❚ do DAG
2. **Via comando:** 
```bash
docker-compose exec airflow-scheduler airflow dags pause azure_devops_card_creation
```

---

## 📊 Dados e Integração

### Q: Atualmente usa dados reais ou falsos?
**R:** **Dados mockados** por enquanto. Para dados reais:
1. Configure conexão SQL Server do Fusion
2. Substitua os dados em `get_pending_tickets()`
3. Implemente queries específicas

### Q: Que formato os tickets devem ter?
**R:** Estrutura obrigatória:
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

### Q: Como evita duplicatas?
**R:** Na etapa `check_existing_cards()`:
1. Para cada ticket, procura work item existente
2. Usa campo customizado "ID Chamado Fusion" para identificar
3. Se encontrar, remove da lista de "novos"
4. Apenas tickets realmente novos vão para criação

### Q: O que acontece se um ticket já foi processado?
**R:** É ignorado automaticamente. O sistema:
1. Verifica se já existe work item com mesmo ID
2. Se existe, pula para próximo ticket
3. Apenas processa tickets realmente novos
4. Evita duplicação

---

## 🐳 Docker e Ambiente

### Q: Por que usar Docker? Não posso instalar direto?
**R:** Docker oferece vantagens:
- ✅ **Isolamento:** Não interfere no seu sistema
- ✅ **Reprodutibilidade:** Funciona igual em qualquer máquina
- ✅ **Versionamento:** Controla versões exatas dos softwares
- ✅ **Facilidade:** Um comando liga tudo

### Q: Consomem muitos recursos do computador?
**R:** Uso moderado:
- **RAM:** ~2GB (aceitável para desenvolvimento)
- **CPU:** Baixo (só picos durante execução)
- **Disco:** ~1GB de imagens Docker
- **Rede:** Apenas para APIs externas

### Q: Como parar tudo se precisar?
**R:** Comando simples:
```bash
# Para todos os containers
docker-compose down

# Para liberar recursos completamente
docker-compose down --volumes --remove-orphans
```

### Q: E se eu quiser atualizar o sistema?
**R:** Processo simples:
1. Pare: `docker-compose down`
2. Atualize o código
3. Reconstrua: `docker-compose up -d --build`

---

## 🚀 Produção e Escala

### Q: Este sistema aguenta quantos tickets?
**R:** Capacidade atual:
- **Limite prático:** ~1000 tickets por execução
- **Gargalo:** API Azure DevOps (rate limit)
- **Otimização:** Pode processar em batches paralelos
- **Escalabilidade:** Airflow suporta múltiplos workers

### Q: Como monitorar em produção?
**R:** Ferramentas disponíveis:
- ✅ **Airflow UI:** http://localhost:8080 (execuções)
- ✅ **Logs:** `docker-compose logs` (detalhes)
- ✅ **Métricas:** Tempo de execução por task
- 📧 **Alertas:** Configuráveis via email/webhook

### Q: E se der erro em produção?
**R:** Sistema tem resiliência:
- 🔄 **Retry:** Tenta 2 vezes automaticamente
- ⏰ **Delay:** Espera 5 minutos entre tentativas
- 📝 **Logs:** Registra tudo para investigação
- 🔔 **Alertas:** Notifica equipe se falhar
- 📊 **Métricas:** Histórico para análise

### Q: Como fazer backup das configurações?
**R:** Elementos importantes:
- 📁 **Código:** Git repository (já versionado)
- 🔐 **Credenciais:** Arquivo `.env` (backup manual)
- ⚙️ **Variables:** `airflow variables export`
- 📊 **Histórico:** Banco PostgreSQL do Airflow

---

## 🔄 Manutenção

### Q: Precisa de manutenção constante?
**R:** Manutenção mínima:
- 🔐 **Tokens:** Renovar anualmente (Azure DevOps)
- 📊 **Logs:** Limpeza ocasional (crescem com tempo)
- 🔄 **Updates:** Atualizações de segurança (opcionais)
- 📈 **Monitoramento:** Verificação semanal de execuções

### Q: Como limpar dados antigos?
**R:** Limpeza automática configurada:
```python
# Em docker-compose.yml, já configurado:
AIRFLOW__CORE__MAX_DAG_RUNS_PER_DAG: 10  # Mantém últimas 10 execuções
```

### Q: Que logs são importantes acompanhar?
**R:** Prioridades:
1. **Errors:** Falhas de conexão ou criação
2. **Success rate:** % de tickets processados com sucesso
3. **Performance:** Tempo de execução por lote
4. **Duplicatas:** Quantos já existiam

---

## 💡 Dicas Avançadas

### Q: Como testar mudanças sem afetar produção?
**R:** Use ambiente de teste:
1. **Dados mockados:** `python test_with_mocks.py`
2. **Projeto teste:** Configure projeto Azure DevOps separado
3. **DAG teste:** Crie cópia do DAG com nome diferente

### Q: Como adicionar campos customizados?
**R:** Edite o método `_build_description()` em `client.py`:
```python
# Adicione campos extras na descrição
description += f"<p><strong>Campo Novo:</strong> {ticket.get('campo_novo')}</p>"
```

### Q: Como configurar notificações por email?
**R:** Configure SMTP no Airflow:
1. Edite `docker-compose.yml`
2. Adicione variáveis de ambiente SMTP
3. Configure `email_on_failure: True` no DAG

Está com alguma dúvida que não foi coberta aqui? Verifique os logs ou consulte a documentação técnica! 🚀
