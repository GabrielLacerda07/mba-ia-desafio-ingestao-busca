# Desafio MBA Engenharia de Software com IA - Full Cycle

Sistema RAG (Retrieval-Augmented Generation) que indexa um PDF no PostgreSQL com pgvector e responde perguntas via chat CLI, usando somente o contexto recuperado do documento.

## Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (o projeto usa `3.12` em `.python-version`)
- Chave de API da [OpenAI](https://platform.openai.com/api-keys)
- Um arquivo PDF para indexar (não incluso no repositório)

## Configuração

### 1. Subir o banco de dados

```bash
docker compose up -d
```

Aguarde o Postgres ficar saudável e o serviço `bootstrap_vector_ext` criar a extensão `vector`.

### 2. Variáveis de ambiente

Na raiz do projeto, copie o exemplo e preencha sua chave OpenAI e o caminho do PDF:

```bash
cp .env.example .env
```

Edite `.env` (o arquivo deve ficar na raiz do projeto):

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `OPENAI_API_KEY` | Sim | Sua chave da OpenAI |
| `PDF_PATH` | Sim | Caminho absoluto para o PDF (recomendado) |
| `DATABASE_URL` | Sim | `postgresql+psycopg://postgres:postgres@localhost:5432/rag` |
| `PG_VECTOR_COLLECTION_NAME` | Sim | Nome da coleção vetorial (ex.: `mba_rag_docs`) |
| `OPENAI_EMBEDDING_MODEL` | Não | Modelo de embedding (padrão: `text-embedding-3-small`) |
| `OPENAI_CHAT_MODEL` | Não | Modelo de chat (padrão: `gpt-4o-mini`) |

> As variáveis `GOOGLE_*` em `.env.example` não são usadas pelo código atual.

### 3. Dependências Python

Na raiz do projeto:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Execução

Execute os comandos a partir da **raiz do projeto**.

### Ingestão (indexar o PDF)

```bash
cd src && python ingest.py
```

Ou, sem entrar em `src/`:

```bash
PYTHONPATH=src python src/ingest.py
```

Saída esperada (resumo): páginas carregadas, chunks gerados e `Ingestão concluída com sucesso.`

Na primeira execução, pode aparecer `Collection not found` — é um aviso normal da biblioteca ao recriar a coleção vazia; não indica falha.

Reexecutar a ingestão **substitui** os dados da coleção (`pre_delete_collection=True`).

### Chat interativo

```bash
cd src && python chat.py
```

Ou:

```bash
PYTHONPATH=src python src/chat.py
```

Comandos para sair: `sair`, `exit` ou `q`.

## Exemplos de uso

**Pergunta sobre o conteúdo do PDF:** a resposta deve citar ou refletir trechos presentes no documento indexado.

**Pergunta fora do contexto** (ex.: "Qual é a capital da França?"):

```
Não tenho informações necessárias para responder sua pergunta.
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError: No module named 'dotenv'` | Ative o venv e rode `pip install -r requirements.txt` |
| `PDF não encontrado em ''` | Defina `PDF_PATH` no `.env` com caminho absoluto |
| `PDF_PATH` inválido | Confirme que o arquivo existe; prefira caminho absoluto |
| `Collection not found` na ingestão | Normal na primeira execução; ignore se terminar com sucesso |
| Coleção vazia / respostas genéricas | Execute `ingest.py` antes do chat |
| Erro de conexão com o banco | Verifique `docker compose up -d` e se `DATABASE_URL` usa `postgresql+psycopg://` |
| Porta 5432 em uso | Pare outro Postgres local ou altere a porta no `docker-compose.yml` |
| Chat não inicia | Confirme `OPENAI_API_KEY`, `DATABASE_URL` e `PG_VECTOR_COLLECTION_NAME` no `.env` |

## Estrutura

- `docker-compose.yml` — Postgres com pgvector e bootstrap da extensão `vector`
- `.env.example` — modelo das variáveis de ambiente
- `src/ingest.py` — carrega PDF, fragmenta e grava embeddings no PGVector
- `src/search.py` — recuperação semântica + prompt RAG + LLM
- `src/chat.py` — loop interativo no terminal
