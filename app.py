import streamlit as st
import os
import unicodedata
import time
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts import PromptTemplate
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# 1. Configuração da Página Web
st.set_page_config(page_title="Agente Financeiro", page_icon="🏦", layout="wide")

# --- O CACHE ---
@st.cache_resource
def carregar_backend():
    load_dotenv()
    
    # Conexão Neo4j
    graph = Neo4jGraph(
        url="bolt://localhost:7687",
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    # LLM (Usando o que funcionou para você)
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    
    # Motor Cypher
    cypher_template = """Você é um especialista em banco de dados Neo4j.
    REGRAS OBRIGATÓRIAS:
    1. Use APENAS os nós e relacionamentos do schema.
    2. Para buscar Estabelecimento (e.nome) ou Categoria (cat.nome), NUNCA use '='. Use SEMPRE: apoc.text.clean(propriedade) CONTAINS apoc.text.clean('valor').
    3. Para o tipo de transação (t.tipo), use EXATAMENTE a igualdade: t.tipo = 'Saída' ou t.tipo = 'Entrada'.
    4. CONTEXTO DE NEGÓCIO DA BASE DE DADOS:
       - O "Salário" ou o que o cliente "ganha" é uma transação de Entrada. Busque assim: apoc.text.clean(cat.nome) CONTAINS apoc.text.clean('salario')
       - Marcas e empresas (Uber, iFood, Netflix) ficam no nó Estabelecimento (e.nome).
    5. REGRA DE IDENTIDADE: O banco de dados já pertence ao usuário atual. NUNCA filtre por ID do cliente (c.id) ou invente IDs falsos como 'meuClienteId'. Apenas faça o MATCH e busque as transações direto.
    6. Retorne APENAS o código Cypher.
    
    Schema:
    {schema}
    Pergunta: {question}
    Query Cypher:"""
    
    cypher_prompt = PromptTemplate(input_variables=["schema", "question"], template=cypher_template)
    chain_neo4j = GraphCypherQAChain.from_llm(
        graph=graph, llm=llm, cypher_prompt=cypher_prompt, verbose=True, allow_dangerous_requests=True 
    )

    # Ferramentas
    @tool
    def consultar_extrato(pergunta: str) -> str:
        """Use esta ferramenta SEMPRE que precisar consultar o histórico financeiro do usuário. Repasse a pergunta EXATAMENTE como ele fez."""
        resposta = chain_neo4j.invoke({"query": pergunta})
        return resposta['result']

    @tool
    def simular_parcelamento(valor_total: float, parcelas: int) -> str:
        """Use para simular ou calcular parcelamento de dívida/compra."""
        taxa = 0.03
        montante = valor_total * ((1 + taxa) ** parcelas)
        valor_parcela = montante / parcelas
        return f"O valor total com juros será R$ {montante:.2f}, dividido em {parcelas}x de R$ {valor_parcela:.2f}."

    ferramentas = [consultar_extrato, simular_parcelamento]

    # Cérebro do Agente
    instrucoes_sistema = """Você é um Consultor Financeiro Inteligente do Itaú. 
    Sempre analise o que o usuário pediu e escolha a ferramenta correta. 
    1. Se precisar de cálculo, use a ferramenta de parcelamento. NUNCA faça de cabeça.
    2. NUNCA adicione tags como '<|channel|>commentary'. Use APENAS o nome exato da ferramenta.
    Seja direto e prestativo."""
    
    memoria = MemorySaver()
    agente = create_react_agent(llm, ferramentas, prompt=instrucoes_sistema, checkpointer=memoria)

    # Motor FAISS (Cache)
    modelo_vetorial = SentenceTransformer('all-MiniLM-L6-v2')
    indice_faiss = faiss.IndexFlatIP(384)
    memoria_cache = []

    return agente, modelo_vetorial, indice_faiss, memoria_cache

# --- INICIALIZAÇÃO DA INFRAESTRUTURA ---
agente_executor, modelo_vetorial, indice_faiss, memoria_cache = carregar_backend()
config_sessao = {"configurable": {"thread_id": "sessao_luis_web_01"}}
LIMIAR_SEMANTICO = 0.90

def limpar_texto(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

# --- INTERFACE GRÁFICA ---
# Barra lateral para impressionar os jurados
with st.sidebar:
    st.image("https://i.pinimg.com/474x/47/b8/66/47b8664ac30573831e28a21909f28b99.jpg", width=150)
    st.markdown("### Engine de IA")
    st.success("Neo4j Graph Database Ativo")
    st.success("lama 3 via Groq API Ativo")
    st.info(f"Cache FAISS: {indice_faiss.ntotal} memórias salvas")

st.title("Consultor Financeiro Inteligente")

# Histórico da interface
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- LÓGICA DE INTERCEPTAÇÃO (O LOOP) ---
pergunta_usuario = st.chat_input("Pergunte sobre seus gastos ou simule parcelamentos...")

if pergunta_usuario:
    # 1. Mostra a pergunta na tela
    with st.chat_message("user"):
        st.markdown(pergunta_usuario)
    st.session_state.mensagens.append({"role": "user", "content": pergunta_usuario})
    
    # 2. Roteamento (Cache vs Agente)
    pergunta_limpa = limpar_texto(pergunta_usuario)
    vetor_pergunta = modelo_vetorial.encode([pergunta_limpa])
    faiss.normalize_L2(vetor_pergunta)
    
    usou_cache = False
    resultado_ia = ""
    
    if indice_faiss.ntotal > 0:
        similaridades, indices = indice_faiss.search(vetor_pergunta, 1)
        score = similaridades[0][0]
        if score >= LIMIAR_SEMANTICO:
            resultado_ia = memoria_cache[indices[0][0]]
            usou_cache = True
            # Mostra um alerta pop-up de alta tecnologia na tela
            st.toast(f"⚡ Resposta instantânea! Cache Semântico atingido ({score*100:.1f}%)", icon="🚀")
            
    if not usou_cache:
        # A "rodinha" de carregamento aparece enquanto a IA pensa
        with st.spinner("Analisando banco de grafos e raciocinando..."):
            resposta = agente_executor.invoke({"messages": [("human", pergunta_limpa)]}, config=config_sessao)
            resultado_ia = resposta["messages"][-1].content
            
            # Aprende a resposta nova
            indice_faiss.add(vetor_pergunta)
            memoria_cache.append(resultado_ia)

    # 3. Imprime a resposta da IA na tela
    with st.chat_message("assistant"):
        st.markdown(resultado_ia)
    st.session_state.mensagens.append({"role": "assistant", "content": resultado_ia})