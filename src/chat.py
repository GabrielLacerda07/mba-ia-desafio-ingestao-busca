from search import search_prompt


def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Chat RAG iniciado. Digite 'sair' para encerrar.")
    while True:
        pergunta = input("\nPergunta: ").strip()
        if not pergunta:
            continue
        if pergunta.lower() in ("sair", "exit", "q"):
            break
        try:
            resposta = chain.invoke({"pergunta": pergunta})
            print(f"\nResposta: {resposta}")
        except Exception as e:
            print(f"Erro ao processar pergunta: {e}")


if __name__ == "__main__":
    main()
