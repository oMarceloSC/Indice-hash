import math

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
    numero_buckets = math.floor(numero_registros / capacidade_bucket) +1

    return numero_buckets

def criar_buckets(numero_buckets):
    buckets = []

    for _ in range(numero_buckets):
        buckets.append([])

    return buckets

def mostrar_paginas(paginas):
    print("\nRESULTADO")

    print(f"Quantidade total de páginas: {len(paginas)}")

    print("\nPrimeira Página")
    print(f"Número da página: 0")

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

    paginas = dividir_em_paginas(palavras, tamanho_pagina)

    mostrar_paginas(paginas)

    NR = len (palavras)

    NB = calcular_buckets(NR, FR)

    buckets = criar_buckets(NB)

    print("\nÍNDICE HASH")

    print(f"NR - Número de registros: {NR}")
    print(f"FR - Capacidade do bucket: {FR}")
    print(f"NB - Número de buckets: {NB}")
    print(f"Buckets criados: {len(buckets)}")