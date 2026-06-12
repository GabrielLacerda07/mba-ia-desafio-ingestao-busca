import os
import sys

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")


def _get_embeddings():
    if not OPENAI_API_KEY:
        print("Erro: OPENAI_API_KEY não configurada.")
        sys.exit(1)
    if not DATABASE_URL or not PG_VECTOR_COLLECTION_NAME:
        print("Erro: DATABASE_URL e PG_VECTOR_COLLECTION_NAME são obrigatórios.")
        sys.exit(1)
    return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)


def ingest_pdf():
    if not PDF_PATH or not os.path.isfile(PDF_PATH):
        print(f"Erro: PDF não encontrado em '{PDF_PATH}'.")
        sys.exit(1)

    embeddings = _get_embeddings()

    print(f"Carregando PDF: {PDF_PATH}")
    docs = PyPDFLoader(PDF_PATH).load()
    print(f"Páginas carregadas: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(docs)
    print(f"Chunks gerados: {len(chunks)}")

    print(f"Indexando na coleção '{PG_VECTOR_COLLECTION_NAME}'...")
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
        pre_delete_collection=True,
    )
    print("Ingestão concluída com sucesso.")


if __name__ == "__main__":
    ingest_pdf()
