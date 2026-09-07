import math
import time


def carregar_palavras(caminho_arquivo):
    palavras = []

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                palavra = linha.strip()

                if palavra:
                    palavras.append(palavra)

        return palavras

    except FileNotFoundError:
        print("Erro: arquivo não encontrado.")
        return []

    except Exception as erro:
        print(f"Erro ao ler o arquivo: {erro}")
        return []


def obter_tamanho_pagina():
    while True:
        try:
            tamanho = int(input("Digite o tamanho da página: "))

            if tamanho > 0:
                return tamanho
            else:
                print("O tamanho da página deve ser maior que zero")

        except ValueError:
            print("Digite apenas números inteiros.")


def dividir_em_paginas(palavras, tamanho_pagina):
    paginas = []

    for i in range(0, len(palavras), tamanho_pagina):
        pagina = palavras[i:i + tamanho_pagina]
        paginas.append(pagina)

    return paginas


def calcular_buckets(numero_registros, capacidade_bucket):
    numero_buckets = math.floor(numero_registros / capacidade_bucket) + 1

    return numero_buckets


def criar_buckets(numero_buckets):
    buckets = []

    for _ in range(numero_buckets):
        buckets.append([])

    return buckets


def criar_overflows(numero_buckets):
    overflows = []

    for _ in range(numero_buckets):
        overflows.append([])

    return overflows


def func_hash(chave, numero_buckets):
    valor_hash = 0

    for carac in chave:
        valor_hash = (valor_hash * 31 + ord(carac)) % numero_buckets

    return valor_hash


def construir_indice(
    paginas,
    buckets,
    overflows,
    numero_buckets,
    capacidade_bucket
):
    inicio = time.perf_counter()

    total_colisoes = 0
    buckets_com_overflow = set()

    for numero_pagina, pagina in enumerate(paginas):
        for palavra in pagina:
            endereco_bucket = func_hash(
                palavra,
                numero_buckets
            )

            registro_indice = (
                palavra,
                numero_pagina
            )

            if len(buckets[endereco_bucket]) < capacidade_bucket:
                buckets[endereco_bucket].append(
                    registro_indice
                )

            else:
                total_colisoes += 1

                overflows[endereco_bucket].append(
                    registro_indice
                )

                buckets_com_overflow.add(
                    endereco_bucket
                )

    fim = time.perf_counter()

    tempo_construcao = fim - inicio

    return (
        tempo_construcao,
        total_colisoes,
        len(buckets_com_overflow)
    )


def buscar_indice(
    chave,
    buckets,
    overflows,
    paginas,
    numero_buckets
):
    inicio = time.perf_counter()

    endereco_bucket = func_hash(
        chave,
        numero_buckets
    )

    pagina_encontrada = None

    for palavra, numero_pagina in buckets[endereco_bucket]:
        if palavra == chave:
            pagina_encontrada = numero_pagina
            break

    if pagina_encontrada is None:
        for palavra, numero_pagina in overflows[endereco_bucket]:
            if palavra == chave:
                pagina_encontrada = numero_pagina
                break

    custo_paginas = 0

    if pagina_encontrada is not None:
        custo_paginas = 1

        pagina = paginas[pagina_encontrada]

        if chave in pagina:
            encontrado = True
        else:
            encontrado = False

    else:
        encontrado = False

    fim = time.perf_counter()

    tempo_busca = fim - inicio

    return (
        encontrado,
        endereco_bucket,
        pagina_encontrada,
        custo_paginas,
        tempo_busca
    )


def mostrar_paginas(paginas):
    print("\nRESULTADO")

    print(f"Quantidade total de páginas: {len(paginas)}")

    print("\nPrimeira Página")
    print("Número da página: 0")

    for palavra in paginas[0][:5]:
        print(palavra)

    print("\nÚltima Página")

    numero_ultima = len(paginas) - 1

    print(f"Número da página: {numero_ultima}")

    for palavra in paginas[-1][:5]:
        print(palavra)


caminho = "../data/words.txt"

FR = 10

palavras = carregar_palavras(caminho)

if palavras:
    print(f"Total de palavras carregadas: {len(palavras)}")

    tamanho_pagina = obter_tamanho_pagina()

    paginas = dividir_em_paginas(palavras,tamanho_pagina)

    mostrar_paginas(paginas)

    NR = len(palavras)

    NB = calcular_buckets(NR,FR)

    buckets = criar_buckets(NB)

    overflows = criar_overflows(NB)

    print("\nÍNDICE HASH")

    print(f"NR - Número de registros: {NR}")

    print(f"FR - Capacidade do bucket: {FR}")

    print(f"NB - Número de buckets: {NB}")

    print(f"Buckets criados: {len(buckets)}")

    (tempo_construcao, total_colisoes, total_buckets_overflow) = construir_indice(paginas, buckets, overflows, NB, FR)

    taxa_colisoes = (total_colisoes / NR) * 100

    taxa_overflow = (total_buckets_overflow / NB) * 100

    print(
        f"Tempo de construção do índice: "
        f"{tempo_construcao:.6f} segundos")

    print("\nESTATÍSTICAS")

    print(f"Total de colisões: {total_colisoes}")

    print(f"Taxa de colisões: {taxa_colisoes:.2f}%")

    print(
        f"Buckets com overflow: "
        f"{total_buckets_overflow}")

    print(
        f"Taxa de overflow: "
        f"{taxa_overflow:.2f}%")

    print("\nBUSCA PELO ÍNDICE")

    chave_busca = input("Digite uma palavra para buscar: ").strip()

    (encontrado,endereco_bucket,pagina_encontrada,custo_paginas,tempo_busca) = buscar_indice(chave_busca, buckets, overflows, paginas, NB)

    print(f"\nBucket acessado: {endereco_bucket}")

    if encontrado:
        print("Chave encontrada.")

        print(f"Página: {pagina_encontrada}")

        print(f"Custo estimado: " 
              f"{custo_paginas} página(s) lida(s)")

    else:
        print("Chave não encontrada.")

        print(f"Custo estimado: " 
              f"{custo_paginas} página(s) lida(s)")

    print(f"Tempo da busca pelo índice: " 
          f"{tempo_busca:.8f} segundos")