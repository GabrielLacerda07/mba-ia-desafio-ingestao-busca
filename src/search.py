import os
from operator import itemgetter

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def _format_docs(docs):
    return "\n\n---\n\n".join(d.page_content for d in docs)


def _build_chain():
    if not OPENAI_API_KEY or not DATABASE_URL or not PG_VECTOR_COLLECTION_NAME:
        return None

    try:
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=PG_VECTOR_COLLECTION_NAME,
            connection=DATABASE_URL,
            use_jsonb=True,
        )
        retriever = vector_store.as_retriever(search_kwargs={"k": 10})
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        llm = ChatOpenAI(model=OPENAI_CHAT_MODEL, temperature=0)

        chain = (
            {
                "contexto": itemgetter("pergunta") | retriever | _format_docs,
                "pergunta": itemgetter("pergunta"),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain
    except Exception as e:
        print(f"Erro ao inicializar busca: {e}")
        return None


def search_prompt(question=None):
    chain = _build_chain()
    if chain is None:
        return None
    if question is not None:
        return chain.invoke({"pergunta": question})
    return chain
