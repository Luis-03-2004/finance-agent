# AAssistente Financeiro (GraphRAG + ReAct Agent)

Este projeto evoluiu de um MVP de GraphRAG para uma arquitetura de **Agente Autônomo (ReAct)**. O assistente financeiro permite que o usuário consulte seu extrato bancário (buscando dados em um grafo), faça simulações matemáticas e mantenha o contexto da conversa, tudo através de uma interface web fluida com latência otimizada por cache semântico.

## Arquitetura e Stack Tecnológica
* **Frontend:** [Streamlit](https://streamlit.io/) para a interface de chat interativa e reativa.
* **Orquestração de IA (O Gerente):** [LangGraph](https://langchain-ai.github.io/langgraph/) implementando o padrão ReAct com memória de sessão (`MemorySaver`).
* **Ferramentas (Tools):** 
  * `consultar_extrato`: Graph Cypher QA Chain delegada a um especialista.
  * `simular_parcelamento`: Ferramenta Python de cálculo de juros compostos.
* **Cache Semântico (O Porteiro):** FAISS e `sentence-transformers` (MiniLM) para interceptar perguntas repetidas, reduzindo o tempo de resposta de ~2.5s para 0.01s.
* **Banco de Dados (O Cofre):** Neo4j (Graph Database) rodando localmente via Docker.
* **LLM:** Llama 3 (via Groq API) - Escolhido pela alta precisão lógica na geração de código Cypher e Tool Calling preciso.

## Estrutura do Projeto
1. `create_data.ipynb`: Script Pandas para gerar um extrato bancário sintético realista.
2. `ingestao_neo4j.ipynb`: Pipeline que estrutura os dados em nós (`Cliente`, `Transacao`, `Estabelecimento`, `Categoria`) e relacionamentos no Neo4j.
3. `app.py`: A aplicação web principal consolidada (Streamlit + Agente LangGraph + Cache FAISS).
4. `requirements.txt`: Lista de dependências para rodar a aplicação.
*(Os notebooks `agente_groq.ipynb` e `agente_react.ipynb` foram mantidos apenas como laboratórios de estudo histórico).*

## Como Executar o Projeto

### 1. Pré-requisitos
* **Python** (versão 3.10 ou superior)
* **Docker** e **Docker Compose** instalados na máquina
* Conta gratuita na [Groq](https://console.groq.com/) para geração da API Key

### 2. Configuração do Ambiente Virtual
Clone este repositório e crie um ambiente virtual Python isolado:
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd hacka-training

# Criação do ambiente virtual
python -m venv .venv

# Ativação do ambiente (Linux/macOS)
source .venv/bin/activate
# No Windows, use: .venv\Scripts\activate

### 3. Instalação das Dependências
Com o ambiente ativado, instale todas as bibliotecas a partir do arquivo de requisitos:
```bash
pip install -r requirements.txt
```

### 4. Configuração das Chaves de API e Variáveis de Ambiente
O projeto utiliza um arquivo `.env` para ocultar dados sensíveis.
1. Crie a sua chave de API gratuita acessando o Console da Groq.
2. Duplique o arquivo de exemplo e renomeie para .env:
```bash
cp .env.example .env
```
3. Abra o arquivo `.env` recém-criado e cole a sua chave `GROQ_API_KEY`. As senhas padrão do Neo4j já estão preenchidas.

### 5. Subindo o Banco de Dados (Neo4j)
Inicie o contêiner Docker que hospeda o Neo4j com o plugin APOC habilitado:
```bash
docker compose up -d
```
O banco estará acessível na porta 7474 (interface web) e 7687 (conexão bolt).

### 6. Preparando os Dados
Abra sua IDE (como VS Code), certifique-se de que o kernel do Jupyter está usando o seu `.venv` e popule o banco rodando os notebooks na seguinte ordem:
1. Execute `create_data.ipynb`
2. Execute `ingestao_neo4j.ipynb`

### 7. Inicializando o Assistente Web
Com os dados no banco, inicie a interface do chat rodando o Streamlit pelo terminal:
```bash
streamlit run app.py
```
O aplicativo abrirá automaticamente no seu navegador em http://localhost:8501.