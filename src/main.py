import math
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

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
        return []

    except Exception:
        return []

def dividir_em_paginas(palavras, tamanho_pagina):
    numero_paginas = math.ceil(len(palavras) / tamanho_pagina)

    paginas = []

    # Primeiro cria todas as páginas vazias
    for _ in range(numero_paginas):
        paginas.append([])

    # Depois carrega os registros nas páginas
    for indice, palavra in enumerate(palavras):
        numero_pagina = indice // tamanho_pagina
        paginas[numero_pagina].append(palavra)

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

def construir_indice(paginas, buckets, overflows, numero_buckets, capacidade_bucket):
    inicio = time.perf_counter()

    total_colisoes = 0
    buckets_com_overflow = set()

    for numero_pagina, pagina in enumerate(paginas):
        for palavra in pagina:
            endereco_bucket = func_hash(palavra, numero_buckets)

            registro_indice = (palavra, numero_pagina)

            if len(buckets[endereco_bucket]) < capacidade_bucket:
                buckets[endereco_bucket].append(registro_indice)

            else:
                total_colisoes += 1

                overflows[endereco_bucket].append(registro_indice)

                buckets_com_overflow.add(endereco_bucket)

    fim = time.perf_counter()

    tempo_construcao = fim - inicio

    return tempo_construcao, total_colisoes, len(buckets_com_overflow)

def buscar_indice(chave, buckets, overflows, paginas, numero_buckets):
    inicio = time.perf_counter()

    endereco_bucket = func_hash(chave, numero_buckets)

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

    return encontrado, endereco_bucket, pagina_encontrada, custo_paginas, tempo_busca

def table_scan(chave, paginas):
    inicio = time.perf_counter()

    paginas_lidas = 0
    registros_lidos = []

    for numero_pagina, pagina in enumerate(paginas):
        paginas_lidas += 1

        for palavra in pagina:
            registros_lidos.append((numero_pagina, palavra))

            if palavra == chave:
                fim = time.perf_counter()

                tempo_busca = fim - inicio

                return True, numero_pagina, paginas_lidas, tempo_busca, registros_lidos

    fim = time.perf_counter()

    tempo_busca = fim - inicio

    return False, None, paginas_lidas, tempo_busca, registros_lidos

def atualizar_status(texto):
    label_status_geral.config(text=texto)


def limpar_texto(widget):
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.config(state="disabled")


def inserir_texto(widget, texto):
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert(tk.END, texto)
    widget.config(state="disabled")


def resetar_comparacao():
    global ultima_busca_indice
    global ultimo_table_scan

    ultima_busca_indice = None
    ultimo_table_scan = None

    label_comparacao_status.config(text="Execute a busca pelo índice e o Table Scan.")
    label_comparacao_tempo.config(text="Diferença de tempo: -")
    label_comparacao_paginas.config(text="Diferença de páginas: -")
    label_percentual_tempo.config(text="Diferença percentual de tempo: -")
    label_percentual_paginas.config(text="Diferença percentual de páginas: -")


def resetar_resultados_busca():
    label_busca_status.config(text="Nenhuma busca realizada")
    label_bucket_busca.config(text="Bucket acessado: -")
    label_pagina_busca.config(text="Página encontrada: -")
    label_custo_busca.config(text="Custo estimado: -")
    label_tempo_busca.config(text="Tempo da busca: -")
    label_processo_busca.config(text="Processo: -")

    label_scan_status.config(text="Table Scan ainda não executado")
    label_scan_pagina.config(text="Página encontrada: -")
    label_scan_paginas_lidas.config(text="Páginas lidas: -")
    label_scan_tempo.config(text="Tempo do Table Scan: -")

    limpar_texto(texto_registros_scan)
    limpar_texto(texto_pagina_acessada)

    frame_bucket_visual.config(highlightbackground="gray")
    frame_pagina_acessada.config(highlightbackground="gray")

    resetar_comparacao()


def resetar_indice():
    global buckets
    global overflows
    global NR
    global NB
    global indice_construido
    global tempo_construcao_indice
    global total_colisoes_indice
    global total_buckets_overflow_indice

    buckets = []
    overflows = []

    NR = 0
    NB = 0

    indice_construido = False

    tempo_construcao_indice = 0
    total_colisoes_indice = 0
    total_buckets_overflow_indice = 0

    label_indice_status.config(text="Índice ainda não construído")
    label_nr.config(text="NR - Número de registros: 0")
    label_nb.config(text="NB - Número de buckets: 0")
    label_tempo_construcao.config(text="Tempo de construção: 0 segundos")
    label_colisoes.config(text="Total de colisões: 0")
    label_taxa_colisoes.config(text="Taxa de colisões: 0.00%")
    label_overflow.config(text="Buckets com overflow: 0")
    label_taxa_overflow.config(text="Taxa de overflow: 0.00%")

    entrada_bucket.delete(0, tk.END)

    limpar_texto(texto_bucket)

    resetar_resultados_busca()

    atualizar_estado_botoes_busca()


def resetar_paginas_e_indice():
    global paginas

    paginas = []

    label_total_paginas.config(text="Quantidade total de páginas: 0")

    texto_primeira_pagina.config(text="Nenhuma página criada")
    texto_ultima_pagina.config(text="Nenhuma página criada")

    resetar_indice()

def atualizar_informacao_arquivo():
    if palavras:
        nome = Path(caminho_arquivo_atual).name

        label_arquivo.config(
            text=f"Arquivo carregado: {nome} | {len(palavras)} palavras"
        )
    else:
        label_arquivo.config(text="Nenhum arquivo válido carregado")


def selecionar_arquivo_interface():
    global palavras
    global caminho_arquivo_atual

    caminho = filedialog.askopenfilename(
        title="Selecionar arquivo TXT",
        filetypes=[("Arquivos de texto", "*.txt")]
    )

    if not caminho:
        return

    novas_palavras = carregar_palavras(caminho)

    if not novas_palavras:
        atualizar_status("Erro: o arquivo está vazio ou não pôde ser lido.")
        return

    palavras = novas_palavras
    caminho_arquivo_atual = caminho

    atualizar_informacao_arquivo()

    resetar_paginas_e_indice()

    atualizar_status("Arquivo carregado com sucesso.")

def mostrar_paginas_interface():
    if not paginas:
        return

    primeira_pagina = paginas[0]
    ultima_pagina = paginas[-1]

    numero_ultima = len(paginas) - 1

    texto_primeira = "Página 0\n\n"

    for palavra in primeira_pagina[:5]:
        texto_primeira += palavra + "\n"

    texto_ultima = f"Página {numero_ultima}\n\n"

    for palavra in ultima_pagina[:5]:
        texto_ultima += palavra + "\n"

    texto_primeira_pagina.config(text=texto_primeira)
    texto_ultima_pagina.config(text=texto_ultima)


def criar_paginas_interface():
    global paginas

    if not palavras:
        atualizar_status("Erro: carregue um arquivo de palavras.")
        return

    try:
        tamanho_pagina = int(entrada_tamanho_pagina.get())

        if tamanho_pagina <= 0:
            atualizar_status("Erro: o tamanho da página deve ser maior que zero.")
            return

    except ValueError:
        atualizar_status("Erro: digite um número inteiro para o tamanho da página.")
        return

    paginas = dividir_em_paginas(palavras, tamanho_pagina)

    label_total_paginas.config(
        text=f"Quantidade total de páginas: {len(paginas)}"
    )

    mostrar_paginas_interface()

    resetar_indice()

    atualizar_status(
        f"Páginas criadas com sucesso. Total: {len(paginas)}."
    )

def construir_indice_interface():
    global NR
    global NB
    global buckets
    global overflows
    global indice_construido
    global tempo_construcao_indice
    global total_colisoes_indice
    global total_buckets_overflow_indice

    if not paginas:
        atualizar_status("Erro: crie as páginas antes de construir o índice.")
        return

    NR = len(palavras)

    NB = calcular_buckets(NR, FR)

    if NB <= (NR / FR):
        atualizar_status("Erro: o número calculado de buckets é inválido.")
        return

    atualizar_status("Construindo o Índice Hash...")

    janela.update_idletasks()

    buckets = criar_buckets(NB)
    overflows = criar_overflows(NB)

    (
        tempo_construcao_indice,
        total_colisoes_indice,
        total_buckets_overflow_indice
    ) = construir_indice(
        paginas,
        buckets,
        overflows,
        NB,
        FR
    )

    taxa_colisoes = (total_colisoes_indice / NR) * 100
    taxa_overflow = (total_buckets_overflow_indice / NB) * 100

    indice_construido = True

    label_indice_status.config(text="Índice construído com sucesso")

    label_nr.config(text=f"NR - Número de registros: {NR}")
    label_fr.config(text=f"FR - Capacidade do bucket: {FR}")
    label_nb.config(text=f"NB - Número de buckets: {NB}")

    label_tempo_construcao.config(
        text=f"Tempo de construção: {tempo_construcao_indice:.6f} segundos"
    )

    label_colisoes.config(
        text=f"Total de colisões: {total_colisoes_indice}"
    )

    label_taxa_colisoes.config(
        text=f"Taxa de colisões: {taxa_colisoes:.2f}%"
    )

    label_overflow.config(
        text=f"Buckets com overflow: {total_buckets_overflow_indice}"
    )

    label_taxa_overflow.config(
        text=f"Taxa de overflow: {taxa_overflow:.2f}%"
    )

    entrada_bucket.delete(0, tk.END)
    entrada_bucket.insert(0, "0")

    mostrar_bucket_interface(0)

    atualizar_estado_botoes_busca()

    atualizar_status("Índice Hash construído com sucesso.")

def mostrar_bucket_interface(numero_bucket, chave_destaque=None):
    if not indice_construido:
        atualizar_status("Erro: construa o Índice Hash primeiro.")
        return

    if numero_bucket < 0 or numero_bucket >= NB:
        atualizar_status(
            f"Erro: informe um bucket entre 0 e {NB - 1}."
        )
        return

    frame_bucket_visual.config(highlightbackground="orange")

    texto_bucket.config(state="normal")
    texto_bucket.delete("1.0", tk.END)

    texto_bucket.insert(
        tk.END,
        f"Bucket {numero_bucket}\n"
        f"Capacidade principal (FR): {FR}\n\n"
    )

    texto_bucket.insert(
        tk.END,
        f"Área principal ({len(buckets[numero_bucket])}/{FR})\n"
    )

    if buckets[numero_bucket]:
        for palavra, numero_pagina in buckets[numero_bucket]:
            linha = f"{palavra} -> Página {numero_pagina}\n"

            if palavra == chave_destaque:
                texto_bucket.insert(tk.END, linha, "destaque")
            else:
                texto_bucket.insert(tk.END, linha)
    else:
        texto_bucket.insert(tk.END, "Vazio\n")

    texto_bucket.insert(
        tk.END,
        f"\nOverflow ({len(overflows[numero_bucket])} registro(s))\n"
    )

    if overflows[numero_bucket]:
        for palavra, numero_pagina in overflows[numero_bucket]:
            linha = f"{palavra} -> Página {numero_pagina}\n"

            if palavra == chave_destaque:
                texto_bucket.insert(tk.END, linha, "destaque")
            else:
                texto_bucket.insert(tk.END, linha)
    else:
        texto_bucket.insert(tk.END, "Sem overflow\n")

    texto_bucket.config(state="disabled")


def visualizar_bucket_interface():
    if not indice_construido:
        atualizar_status("Erro: construa o Índice Hash primeiro.")
        return

    try:
        numero_bucket = int(entrada_bucket.get())
    except ValueError:
        atualizar_status("Erro: informe um número de bucket válido.")
        return

    mostrar_bucket_interface(numero_bucket)

    atualizar_status(f"Exibindo o bucket {numero_bucket}.")

def mostrar_pagina_acessada(numero_pagina, chave):
    frame_pagina_acessada.config(highlightbackground="orange")

    texto_pagina_acessada.config(state="normal")
    texto_pagina_acessada.delete("1.0", tk.END)

    texto_pagina_acessada.insert(
        tk.END,
        f"Página {numero_pagina}\n\n"
    )

    for palavra in paginas[numero_pagina]:
        if palavra == chave:
            texto_pagina_acessada.insert(
                tk.END,
                f"{palavra}  <- registro encontrado\n",
                "destaque"
            )
        else:
            texto_pagina_acessada.insert(
                tk.END,
                palavra + "\n"
            )

    texto_pagina_acessada.config(state="disabled")

def buscar_indice_interface():
    global ultima_busca_indice

    chave_busca = variavel_busca.get().strip()

    if not chave_busca:
        atualizar_status("Erro: digite uma palavra para buscar.")
        return

    if not indice_construido:
        atualizar_status("Erro: construa o Índice Hash primeiro.")
        return

    (
        encontrado,
        endereco_bucket,
        pagina_encontrada,
        custo_paginas,
        tempo_busca
    ) = buscar_indice(
        chave_busca,
        buckets,
        overflows,
        paginas,
        NB
    )

    label_bucket_busca.config(
        text=f"Bucket acessado: {endereco_bucket}"
    )

    label_custo_busca.config(
        text=f"Custo estimado: {custo_paginas} página(s) lida(s)"
    )

    label_tempo_busca.config(
        text=f"Tempo da busca: {tempo_busca:.8f} segundos"
    )

    entrada_bucket.delete(0, tk.END)
    entrada_bucket.insert(0, str(endereco_bucket))

    mostrar_bucket_interface(
        endereco_bucket,
        chave_busca
    )

    if encontrado:
        label_busca_status.config(text="Chave encontrada")

        label_pagina_busca.config(
            text=f"Página encontrada: {pagina_encontrada}"
        )

        label_processo_busca.config(
            text=(
                f"Processo: {chave_busca} -> "
                f"Hash -> Bucket {endereco_bucket} -> "
                f"Página {pagina_encontrada}"
            )
        )

        mostrar_pagina_acessada(
            pagina_encontrada,
            chave_busca
        )

    else:
        label_busca_status.config(text="Chave não encontrada")
        label_pagina_busca.config(text="Página encontrada: -")

        label_processo_busca.config(
            text=(
                f"Processo: {chave_busca} -> "
                f"Hash -> Bucket {endereco_bucket} -> "
                f"não encontrada"
            )
        )

        limpar_texto(texto_pagina_acessada)

        frame_pagina_acessada.config(
            highlightbackground="gray"
        )

    ultima_busca_indice = {
        "chave": chave_busca,
        "encontrado": encontrado,
        "tempo": tempo_busca,
        "paginas": custo_paginas
    }

    atualizar_comparacao()

    atualizar_status("Busca pelo Índice Hash concluída.")

def mostrar_registros_scan(registros):
    texto_registros_scan.config(state="normal")
    texto_registros_scan.delete("1.0", tk.END)

    linhas = []
    pagina_anterior = None

    for numero_pagina, palavra in registros:
        if numero_pagina != pagina_anterior:
            linhas.append(f"\nPágina {numero_pagina}\n")
            pagina_anterior = numero_pagina

        linhas.append(palavra + "\n")

    texto_registros_scan.insert(
        tk.END,
        "".join(linhas)
    )

    texto_registros_scan.config(state="disabled")


def executar_table_scan_interface():
    global ultimo_table_scan

    chave_busca = variavel_busca.get().strip()

    if not chave_busca:
        atualizar_status("Erro: digite uma palavra para realizar o Table Scan.")
        return

    if not paginas:
        atualizar_status("Erro: crie as páginas antes do Table Scan.")
        return

    atualizar_status("Executando Table Scan...")

    janela.update_idletasks()

    (
        encontrado,
        pagina_encontrada,
        paginas_lidas,
        tempo_scan,
        registros_lidos
    ) = table_scan(
        chave_busca,
        paginas
    )

    if encontrado:
        label_scan_status.config(text="Chave encontrada")

        label_scan_pagina.config(
            text=f"Página encontrada: {pagina_encontrada}"
        )

    else:
        label_scan_status.config(text="Chave não encontrada")
        label_scan_pagina.config(text="Página encontrada: -")

    label_scan_paginas_lidas.config(
        text=f"Páginas lidas: {paginas_lidas}"
    )

    label_scan_tempo.config(
        text=f"Tempo do Table Scan: {tempo_scan:.8f} segundos"
    )

    mostrar_registros_scan(registros_lidos)

    ultimo_table_scan = {
        "chave": chave_busca,
        "encontrado": encontrado,
        "tempo": tempo_scan,
        "paginas": paginas_lidas
    }

    atualizar_comparacao()

    atualizar_status("Table Scan concluído.")

def atualizar_comparacao():
    if ultima_busca_indice is None or ultimo_table_scan is None:
        return

    if ultima_busca_indice["chave"] != ultimo_table_scan["chave"]:
        return

    tempo_indice = ultima_busca_indice["tempo"]
    tempo_scan = ultimo_table_scan["tempo"]

    paginas_indice = ultima_busca_indice["paginas"]
    paginas_scan = ultimo_table_scan["paginas"]

    diferenca_tempo = tempo_scan - tempo_indice
    diferenca_paginas = paginas_scan - paginas_indice

    if tempo_scan > 0:
        percentual_tempo = (
            (tempo_scan - tempo_indice) / tempo_scan
        ) * 100
    else:
        percentual_tempo = 0

    if paginas_scan > 0:
        percentual_paginas = (
            (paginas_scan - paginas_indice) / paginas_scan
        ) * 100
    else:
        percentual_paginas = 0

    label_comparacao_status.config(
        text=f"Comparação para a chave: {ultima_busca_indice['chave']}"
    )

    label_comparacao_tempo.config(
        text=(
            f"Diferença de tempo: "
            f"{diferenca_tempo:.8f} segundos"
        )
    )

    label_comparacao_paginas.config(
        text=(
            f"Diferença de páginas: "
            f"{diferenca_paginas} página(s)"
        )
    )

    label_percentual_tempo.config(
        text=(
            f"Redução percentual de tempo: "
            f"{percentual_tempo:.2f}%"
        )
    )

    label_percentual_paginas.config(
        text=(
            f"Redução percentual de páginas lidas: "
            f"{percentual_paginas:.2f}%"
        )
    )

def atualizar_estado_botoes_busca(*args):
    chave_digitada = variavel_busca.get().strip()

    if chave_digitada and paginas:
        botao_table_scan.config(state="normal")
    else:
        botao_table_scan.config(state="disabled")

    if chave_digitada and indice_construido:
        botao_buscar.config(state="normal")
    else:
        botao_buscar.config(state="disabled")


def chave_busca_alterada(*args):
    global ultima_busca_indice
    global ultimo_table_scan

    ultima_busca_indice = None
    ultimo_table_scan = None

    label_busca_status.config(text="Nenhuma busca realizada")
    label_bucket_busca.config(text="Bucket acessado: -")
    label_pagina_busca.config(text="Página encontrada: -")
    label_custo_busca.config(text="Custo estimado: -")
    label_tempo_busca.config(text="Tempo da busca: -")
    label_processo_busca.config(text="Processo: -")

    label_scan_status.config(text="Table Scan ainda não executado")
    label_scan_pagina.config(text="Página encontrada: -")
    label_scan_paginas_lidas.config(text="Páginas lidas: -")
    label_scan_tempo.config(text="Tempo do Table Scan: -")

    limpar_texto(texto_registros_scan)
    limpar_texto(texto_pagina_acessada)

    resetar_comparacao()

    atualizar_estado_botoes_busca()

CAMINHO_PADRAO = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "words.txt"
)

FR = 10

palavras = carregar_palavras(CAMINHO_PADRAO)

if palavras:
    caminho_arquivo_atual = CAMINHO_PADRAO
else:
    caminho_arquivo_atual = ""

paginas = []

buckets = []
overflows = []

NR = 0
NB = 0

indice_construido = False

tempo_construcao_indice = 0
total_colisoes_indice = 0
total_buckets_overflow_indice = 0

ultima_busca_indice = None
ultimo_table_scan = None

janela = tk.Tk()

janela.title("Simulador de Índice Hash")
janela.geometry("1180x900")
janela.minsize(1000, 700)

frame_principal = tk.Frame(janela)
frame_principal.pack(fill="both", expand=True)

canvas = tk.Canvas(frame_principal)

scrollbar = tk.Scrollbar(
    frame_principal,
    orient="vertical",
    command=canvas.yview
)

conteudo = tk.Frame(canvas)

conteudo.bind(
    "<Configure>",
    lambda evento: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

janela_canvas = canvas.create_window(
    (0, 0),
    window=conteudo,
    anchor="nw"
)

canvas.bind(
    "<Configure>",
    lambda evento: canvas.itemconfigure(
        janela_canvas,
        width=evento.width
    )
)

canvas.configure(
    yscrollcommand=scrollbar.set
)

canvas.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)

titulo = tk.Label(
    conteudo,
    text="Simulador de Índice Hash",
    font=("Arial", 20, "bold")
)

titulo.pack(pady=15)

frame_arquivo = tk.LabelFrame(
    conteudo,
    text="1. Arquivo de Dados",
    width=900,
    height=100
)

frame_arquivo.pack(pady=10)
frame_arquivo.pack_propagate(False)


if palavras:
    texto_arquivo_inicial = (
        f"Arquivo carregado automaticamente: "
        f"words.txt | {len(palavras)} palavras"
    )
else:
    texto_arquivo_inicial = (
        "Arquivo words.txt não encontrado automaticamente"
    )


label_arquivo = tk.Label(
    frame_arquivo,
    text=texto_arquivo_inicial
)

label_arquivo.pack(pady=8)


botao_selecionar_arquivo = tk.Button(
    frame_arquivo,
    text="Selecionar outro arquivo TXT",
    command=selecionar_arquivo_interface
)

botao_selecionar_arquivo.pack()

frame_configuracao_paginas = tk.LabelFrame(
    conteudo,
    text="2. Páginas",
    width=900,
    height=110
)

frame_configuracao_paginas.pack(pady=10)
frame_configuracao_paginas.pack_propagate(False)


frame_entrada_pagina = tk.Frame(
    frame_configuracao_paginas
)

frame_entrada_pagina.pack(pady=10)


label_tamanho = tk.Label(
    frame_entrada_pagina,
    text="Tamanho da página:"
)

label_tamanho.pack(
    side="left",
    padx=5
)


entrada_tamanho_pagina = tk.Entry(
    frame_entrada_pagina,
    width=10
)

entrada_tamanho_pagina.pack(
    side="left",
    padx=5
)


botao_criar_paginas = tk.Button(
    frame_entrada_pagina,
    text="Criar páginas",
    command=criar_paginas_interface
)

botao_criar_paginas.pack(
    side="left",
    padx=10
)


label_total_paginas = tk.Label(
    frame_configuracao_paginas,
    text="Quantidade total de páginas: 0"
)

label_total_paginas.pack()

frame_paginas = tk.Frame(conteudo)
frame_paginas.pack(pady=10)


frame_primeira_pagina = tk.LabelFrame(
    frame_paginas,
    text="Primeira Página",
    width=400,
    height=180
)

frame_primeira_pagina.pack(
    side="left",
    padx=10
)

frame_primeira_pagina.pack_propagate(False)


texto_primeira_pagina = tk.Label(
    frame_primeira_pagina,
    text="Nenhuma página criada",
    justify="left",
    anchor="nw"
)

texto_primeira_pagina.pack(
    padx=15,
    pady=15,
    fill="both",
    expand=True
)


frame_ultima_pagina = tk.LabelFrame(
    frame_paginas,
    text="Última Página",
    width=400,
    height=180
)

frame_ultima_pagina.pack(
    side="left",
    padx=10
)

frame_ultima_pagina.pack_propagate(False)


texto_ultima_pagina = tk.Label(
    frame_ultima_pagina,
    text="Nenhuma página criada",
    justify="left",
    anchor="nw"
)

texto_ultima_pagina.pack(
    padx=15,
    pady=15,
    fill="both",
    expand=True
)

frame_indice = tk.LabelFrame(
    conteudo,
    text="3. Índice Hash",
    width=900,
    height=280
)

frame_indice.pack(pady=10)
frame_indice.pack_propagate(False)


botao_construir_indice = tk.Button(
    frame_indice,
    text="Construir Índice Hash",
    command=construir_indice_interface
)

botao_construir_indice.pack(pady=10)


label_indice_status = tk.Label(
    frame_indice,
    text="Índice ainda não construído",
    font=("Arial", 10, "bold")
)

label_indice_status.pack(pady=5)


frame_estatisticas = tk.Frame(frame_indice)
frame_estatisticas.pack(pady=5)


label_nr = tk.Label(
    frame_estatisticas,
    text="NR - Número de registros: 0"
)

label_nr.grid(
    row=0,
    column=0,
    sticky="w",
    padx=20,
    pady=3
)


label_fr = tk.Label(
    frame_estatisticas,
    text=f"FR - Capacidade do bucket: {FR}"
)

label_fr.grid(
    row=0,
    column=1,
    sticky="w",
    padx=20,
    pady=3
)


label_nb = tk.Label(
    frame_estatisticas,
    text="NB - Número de buckets: 0"
)

label_nb.grid(
    row=1,
    column=0,
    sticky="w",
    padx=20,
    pady=3
)


label_tempo_construcao = tk.Label(
    frame_estatisticas,
    text="Tempo de construção: 0 segundos"
)

label_tempo_construcao.grid(
    row=1,
    column=1,
    sticky="w",
    padx=20,
    pady=3
)


label_colisoes = tk.Label(
    frame_estatisticas,
    text="Total de colisões: 0"
)

label_colisoes.grid(
    row=2,
    column=0,
    sticky="w",
    padx=20,
    pady=3
)


label_taxa_colisoes = tk.Label(
    frame_estatisticas,
    text="Taxa de colisões: 0.00%"
)

label_taxa_colisoes.grid(
    row=2,
    column=1,
    sticky="w",
    padx=20,
    pady=3
)


label_overflow = tk.Label(
    frame_estatisticas,
    text="Buckets com overflow: 0"
)

label_overflow.grid(
    row=3,
    column=0,
    sticky="w",
    padx=20,
    pady=3
)


label_taxa_overflow = tk.Label(
    frame_estatisticas,
    text="Taxa de overflow: 0.00%"
)

label_taxa_overflow.grid(
    row=3,
    column=1,
    sticky="w",
    padx=20,
    pady=3
)

frame_bucket_visual = tk.LabelFrame(
    conteudo,
    text="4. Visualização dos Buckets",
    width=900,
    height=350,
    highlightthickness=3,
    highlightbackground="gray"
)

frame_bucket_visual.pack(pady=10)
frame_bucket_visual.pack_propagate(False)


frame_busca_bucket = tk.Frame(
    frame_bucket_visual
)

frame_busca_bucket.pack(pady=10)


tk.Label(
    frame_busca_bucket,
    text="Número do bucket:"
).pack(
    side="left",
    padx=5
)


entrada_bucket = tk.Entry(
    frame_busca_bucket,
    width=12
)

entrada_bucket.pack(
    side="left",
    padx=5
)


botao_visualizar_bucket = tk.Button(
    frame_busca_bucket,
    text="Visualizar Bucket",
    command=visualizar_bucket_interface
)

botao_visualizar_bucket.pack(
    side="left",
    padx=10
)


frame_texto_bucket = tk.Frame(
    frame_bucket_visual
)

frame_texto_bucket.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)


scroll_bucket = tk.Scrollbar(
    frame_texto_bucket
)

scroll_bucket.pack(
    side="right",
    fill="y"
)


texto_bucket = tk.Text(
    frame_texto_bucket,
    wrap="word",
    yscrollcommand=scroll_bucket.set
)

texto_bucket.pack(
    fill="both",
    expand=True
)

scroll_bucket.config(
    command=texto_bucket.yview
)

texto_bucket.tag_configure(
    "destaque",
    background="yellow",
    font=("Arial", 10, "bold")
)

texto_bucket.config(
    state="disabled"
)

frame_busca = tk.LabelFrame(
    conteudo,
    text="5. Busca pelo Índice Hash",
    width=900,
    height=270
)

frame_busca.pack(pady=10)
frame_busca.pack_propagate(False)


frame_entrada_busca = tk.Frame(frame_busca)
frame_entrada_busca.pack(pady=10)


tk.Label(
    frame_entrada_busca,
    text="Chave:"
).pack(
    side="left",
    padx=5
)


variavel_busca = tk.StringVar()


entrada_busca = tk.Entry(
    frame_entrada_busca,
    width=35,
    textvariable=variavel_busca
)

entrada_busca.pack(
    side="left",
    padx=5
)


botao_buscar = tk.Button(
    frame_entrada_busca,
    text="Buscar pelo Índice",
    command=buscar_indice_interface,
    state="disabled"
)

botao_buscar.pack(
    side="left",
    padx=10
)


label_busca_status = tk.Label(
    frame_busca,
    text="Nenhuma busca realizada",
    font=("Arial", 10, "bold")
)

label_busca_status.pack(pady=5)


frame_resultado_busca = tk.Frame(
    frame_busca
)

frame_resultado_busca.pack(pady=5)


label_bucket_busca = tk.Label(
    frame_resultado_busca,
    text="Bucket acessado: -"
)

label_bucket_busca.grid(
    row=0,
    column=0,
    padx=20,
    pady=3,
    sticky="w"
)


label_pagina_busca = tk.Label(
    frame_resultado_busca,
    text="Página encontrada: -"
)

label_pagina_busca.grid(
    row=0,
    column=1,
    padx=20,
    pady=3,
    sticky="w"
)


label_custo_busca = tk.Label(
    frame_resultado_busca,
    text="Custo estimado: -"
)

label_custo_busca.grid(
    row=1,
    column=0,
    padx=20,
    pady=3,
    sticky="w"
)


label_tempo_busca = tk.Label(
    frame_resultado_busca,
    text="Tempo da busca: -"
)

label_tempo_busca.grid(
    row=1,
    column=1,
    padx=20,
    pady=3,
    sticky="w"
)


label_processo_busca = tk.Label(
    frame_busca,
    text="Processo: -"
)

label_processo_busca.pack(pady=10)

frame_pagina_acessada = tk.LabelFrame(
    conteudo,
    text="6. Página Acessada na Busca",
    width=900,
    height=300,
    highlightthickness=3,
    highlightbackground="gray"
)

frame_pagina_acessada.pack(pady=10)
frame_pagina_acessada.pack_propagate(False)


frame_texto_pagina = tk.Frame(
    frame_pagina_acessada
)

frame_texto_pagina.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


scroll_pagina = tk.Scrollbar(
    frame_texto_pagina
)

scroll_pagina.pack(
    side="right",
    fill="y"
)


texto_pagina_acessada = tk.Text(
    frame_texto_pagina,
    yscrollcommand=scroll_pagina.set
)

texto_pagina_acessada.pack(
    fill="both",
    expand=True
)

scroll_pagina.config(
    command=texto_pagina_acessada.yview
)

texto_pagina_acessada.tag_configure(
    "destaque",
    background="yellow",
    font=("Arial", 10, "bold")
)

texto_pagina_acessada.config(
    state="disabled"
)

frame_scan = tk.LabelFrame(
    conteudo,
    text="7. Table Scan",
    width=900,
    height=520
)

frame_scan.pack(pady=10)
frame_scan.pack_propagate(False)


botao_table_scan = tk.Button(
    frame_scan,
    text="Executar Table Scan",
    command=executar_table_scan_interface,
    state="disabled"
)

botao_table_scan.pack(pady=10)


label_scan_status = tk.Label(
    frame_scan,
    text="Table Scan ainda não executado",
    font=("Arial", 10, "bold")
)

label_scan_status.pack(pady=5)


frame_resultado_scan = tk.Frame(
    frame_scan
)

frame_resultado_scan.pack(pady=5)


label_scan_pagina = tk.Label(
    frame_resultado_scan,
    text="Página encontrada: -"
)

label_scan_pagina.grid(
    row=0,
    column=0,
    padx=20,
    pady=3
)


label_scan_paginas_lidas = tk.Label(
    frame_resultado_scan,
    text="Páginas lidas: -"
)

label_scan_paginas_lidas.grid(
    row=0,
    column=1,
    padx=20,
    pady=3
)


label_scan_tempo = tk.Label(
    frame_scan,
    text="Tempo do Table Scan: -"
)

label_scan_tempo.pack(pady=5)


tk.Label(
    frame_scan,
    text="Registros lidos durante o Table Scan:"
).pack(pady=5)


frame_registros_scan = tk.Frame(
    frame_scan
)

frame_registros_scan.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)


scroll_scan = tk.Scrollbar(
    frame_registros_scan
)

scroll_scan.pack(
    side="right",
    fill="y"
)


texto_registros_scan = tk.Text(
    frame_registros_scan,
    yscrollcommand=scroll_scan.set
)

texto_registros_scan.pack(
    fill="both",
    expand=True
)

scroll_scan.config(
    command=texto_registros_scan.yview
)

texto_registros_scan.config(
    state="disabled"
)


frame_comparacao = tk.LabelFrame(
    conteudo,
    text="8. Comparação: Índice Hash x Table Scan",
    width=900,
    height=210
)

frame_comparacao.pack(pady=10)
frame_comparacao.pack_propagate(False)


label_comparacao_status = tk.Label(
    frame_comparacao,
    text="Execute a busca pelo índice e o Table Scan.",
    font=("Arial", 10, "bold")
)

label_comparacao_status.pack(pady=10)


label_comparacao_tempo = tk.Label(
    frame_comparacao,
    text="Diferença de tempo: -"
)

label_comparacao_tempo.pack(pady=3)


label_comparacao_paginas = tk.Label(
    frame_comparacao,
    text="Diferença de páginas: -"
)

label_comparacao_paginas.pack(pady=3)


label_percentual_tempo = tk.Label(
    frame_comparacao,
    text="Diferença percentual de tempo: -"
)

label_percentual_tempo.pack(pady=3)


label_percentual_paginas = tk.Label(
    frame_comparacao,
    text="Diferença percentual de páginas: -"
)

label_percentual_paginas.pack(pady=3)

frame_status = tk.LabelFrame(
    conteudo,
    text="Status",
    width=900,
    height=80
)

frame_status.pack(
    pady=10
)

frame_status.pack_propagate(False)


if palavras:
    status_inicial = (
        "words.txt identificado automaticamente. "
        "Informe o tamanho da página para começar."
    )
else:
    status_inicial = (
        "words.txt não encontrado. "
        "Selecione um arquivo TXT."
    )


label_status_geral = tk.Label(
    frame_status,
    text=status_inicial,
    font=("Arial", 10, "bold")
)

label_status_geral.pack(
    pady=20
)


variavel_busca.trace_add(
    "write",
    chave_busca_alterada
)

janela.mainloop()