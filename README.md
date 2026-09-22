# Assistente Financeiro (GraphRAG)

Este é um MVP (Produto Mínimo Viável) desenvolvido com o objetivo é criar um assistente financeiro inteligente que utiliza uma arquitetura **GraphRAG**, para que o usuário consulte seu extrato bancário, que é traduzida instantaneamente para consultas em um banco de dados de grafos.

## Stack Tecnológica
* **Banco de Dados:** Neo4j (Graph Database) rodando localmente via Docker.
* **Orquestração de IA:** LangChain.
* **LLM:** Llama 3 (Atualmente via groq API) - Escolhido pela alta precisão lógica na geração de código Cypher e baixíssima latência.
* **Linguagem:** Python (Jupyter Notebooks).

## Estrutura do Projeto
1. `create_data.ipynb`: Script Pandas para gerar um extrato bancário sintético e realista.
2. `ingestao_neo4j.ipynb`: Pipeline que lê os dados e os estrutura em nós (`Cliente`, `Transacao`, `Estabelecimento`, `Categoria`) e relacionamentos no Neo4j.
3. `agente_groq.ipynb`: O cérebro do projeto. Um agente `GraphCypherQAChain` que entende o esquema do banco, traduz a pergunta do usuário para Cypher, executa a busca e formula a resposta natural.

## Como Executar o Projeto

### 1. Pré-requisitos
* **Python** (recomendado versão 3.10 ou superior)
* **Docker** e **Docker Compose** instalados na máquina
* Conta gratuita na [Groq](https://console.groq.com/) para geração da API Key

### 2. Configuração do Ambiente Virtual
Clone este repositório e crie um ambiente virtual Python isolado para instalar as dependências:
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd hacka-training

# Criação do ambiente virtual
python -m venv .venv

# Ativação do ambiente (Linux/macOS)
source .venv/bin/activate
# Se estiver no Windows, use: .venv\Scripts\activate
```

### 3. Instalação das Dependências
Com o ambiente ativado, instale as bibliotecas necessárias:
```bash
pip install langchain langchain-neo4j langchain-groq python-dotenv pandas jupyter
```

### 4. Configuração das Chaves de API e Variáveis de Ambiente
O projeto utiliza um arquivo .env para ocultar dados sensíveis.

1. Crie a sua chave de API gratuita acessando o [Console da Groq](https://console.groq.com/?utm_source=gemini)
2. Duplique o arquivo de exemplo e renomeie para .env:
```bash
cp .env.example .env
```
3. Abra o arquivo .env recém-criado e cole a sua chave GROQ_API_KEY. As senhas padrão do Neo4j já estão preenchidas.

### 5. Subindo o Banco de Dados (Neo4j)
Inicie o contêiner Docker que hospeda o Neo4j com o plugin APOC habilitado:
```bash
docker compose up -d
```
O banco estará acessível na porta 7474 (interface web) e 7687 (conexão bolt).

### 6. Execução da Pipeline
Abra sua IDE (como VS Code), certifique-se de que o kernel do Jupyter está usando o seu `.venv`, e execute os notebooks na seguinte ordem:

1. Rodar `create_data.ipynb`
2. Rodar `ingestao_neo4j.ipynb`
3. Rodar `agente_groq.ipynb` para interagir com o agente financeiro.
