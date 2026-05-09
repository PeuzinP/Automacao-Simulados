import os
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from omr_reader import processar_imagens_omr
from painel_correcao_omr import abrir_painel_correcao_omr


# =========================
# CONFIGURAÇÕES VISUAIS
# =========================

COR_FUNDO = "#F4F6FA"
COR_CARD = "#FFFFFF"
COR_TEXTO = "#132342"
COR_TEXTO_SUAVE = "#5F6B7A"
COR_AZUL = "#14387F"
COR_AZUL_ESCURO = "#132342"
COR_AMARELO = "#F7CD23"
COR_BORDA = "#D9DEE8"
COR_SUCESSO = "#1E8E3E"
COR_ALERTA = "#D97706"


pasta_projeto = os.getcwd()
ultimo_processamento = None


# =========================
# FUNÇÕES AUXILIARES
# =========================

def escrever_log(texto):
    caixa_log.configure(state="normal")
    caixa_log.insert(tk.END, texto + "\n")
    caixa_log.see(tk.END)
    caixa_log.configure(state="disabled")
    janela.update_idletasks()


def limpar_log():
    caixa_log.configure(state="normal")
    caixa_log.delete("1.0", tk.END)
    caixa_log.configure(state="disabled")


def definir_status(texto):
    lbl_status.config(text=texto)
    janela.update_idletasks()


def escolher_pasta():
    global pasta_projeto

    pasta = filedialog.askdirectory()

    if pasta:
        pasta_projeto = pasta
        entry_pasta.configure(state="normal")
        entry_pasta.delete(0, tk.END)
        entry_pasta.insert(0, pasta)
        entry_pasta.configure(state="readonly")

        escrever_log(f"Pasta do projeto alterada para: {pasta}")

def atualizar_progresso(valor, total, mensagem=""):
    def aplicar():
        if total <= 0:
            progress_var.set(0)
            lbl_progresso.config(text="0%  |  Nenhuma imagem encontrada.")
            return

        percentual = int((valor / total) * 100)
        percentual = max(0, min(percentual, 100))

        progress_var.set(percentual)

        if mensagem:
            lbl_progresso.config(text=f"{percentual}%  |  {mensagem}")
            escrever_log(mensagem)
        else:
            lbl_progresso.config(text=f"{percentual}%")

        janela.update_idletasks()

    janela.after(0, aplicar)


def resetar_progresso():
    progress_var.set(0)
    lbl_progresso.config(text="0%  |  Aguardando processamento...")
    janela.update_idletasks()

def abrir_pasta(caminho):
    if os.path.exists(caminho):
        os.startfile(caminho)
    else:
        messagebox.showerror("Erro", f"Pasta não encontrada:\n{caminho}")


def abrir_saida():
    abrir_pasta(os.path.join(pasta_projeto, "saida"))


def abrir_ultimo_processamento():
    global ultimo_processamento

    if ultimo_processamento and os.path.exists(ultimo_processamento):
        abrir_pasta(ultimo_processamento)
        return

    pasta_saida = os.path.join(pasta_projeto, "saida")

    if not os.path.exists(pasta_saida):
        messagebox.showwarning(
            "Último processamento",
            "Nenhuma pasta de saída encontrada ainda."
        )
        return

    processamentos = [
        os.path.join(pasta_saida, nome)
        for nome in os.listdir(pasta_saida)
        if nome.startswith("processamento_")
        and os.path.isdir(os.path.join(pasta_saida, nome))
    ]

    if not processamentos:
        messagebox.showwarning(
            "Último processamento",
            "Nenhum processamento encontrado em saida."
        )
        return

    processamentos.sort(reverse=True)
    abrir_pasta(processamentos[0])


def executar_comando(comando, mensagem_inicio):
    limpar_log()
    definir_status(mensagem_inicio)
    escrever_log(mensagem_inicio)

    try:
        processo = subprocess.Popen(
            comando,
            cwd=pasta_projeto,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )

        for linha in processo.stdout:
            escrever_log(linha.strip())

        processo.wait()

        if processo.returncode == 0:
            escrever_log("Processo concluído com sucesso.")
            definir_status("Processo concluído com sucesso.")
        else:
            escrever_log("Processo finalizado com erro.")
            definir_status("Processo finalizado com erro.")

    except Exception as e:
        escrever_log(f"Erro: {e}")
        definir_status("Erro durante o processo.")


# =========================
# AÇÕES PRINCIPAIS
# =========================

def atualizar_base():
    thread = threading.Thread(
        target=executar_comando,
        args=("python atualizar_base.py", "Atualizando base de alunos..."),
        daemon=True
    )
    thread.start()


def abrir_painel_validacao():
    try:
        definir_status("Abrindo painel de validação...")
        escrever_log("Abrindo painel de validação OCR...")

        subprocess.Popen(
            "python painel_validacao.py",
            cwd=pasta_projeto,
            shell=True
        )

    except Exception as e:
        messagebox.showerror("Erro", str(e))
        definir_status("Erro ao abrir painel de validação.")


def selecionar_imagens_omr():
    pasta = filedialog.askdirectory(
        title="Selecione a pasta com as imagens OMR"
    )

    if not pasta:
        return

    thread = threading.Thread(
        target=executar_leitura_omr_em_thread,
        args=(pasta,),
        daemon=True
    )
    thread.start()
    
def executar_leitura_omr_em_thread(pasta):
    global ultimo_processamento

    try:
        janela.after(0, limpar_log)
        janela.after(0, resetar_progresso)
        janela.after(0, lambda: definir_status("Lendo cartões OMR..."))
        janela.after(0, lambda: escrever_log("Iniciando leitura OMR..."))
        janela.after(0, lambda: escrever_log(f"Pasta selecionada: {pasta}"))
        janela.after(0, lambda: btn_omr.config(state="disabled"))

        resultado = processar_imagens_omr(
            pasta,
            progresso_callback=atualizar_progresso
        )

        ultimo_processamento = (
            resultado.get("pasta_processamento")
            or resultado.get("pasta_execucao")
        )

        def finalizar_interface():
            escrever_log(f"Total de imagens encontradas: {resultado['total_imagens']}")
            escrever_log(f"Total com leitura OK: {resultado['total_ok']}")
            escrever_log(f"Total enviado para conferência: {resultado['total_manual']}")
            escrever_log(f"Log gerado em: {resultado['log']}")

            if resultado.get("leituras_omr"):
                escrever_log(f"Leituras OMR: {resultado['leituras_omr']}")

            definir_status("Leitura concluída. Abrindo painel de conferência...")
            progress_var.set(100)
            lbl_progresso.config(text="100%  |  Processamento concluído.")
            btn_omr.config(state="normal")
            janela.update_idletasks()

            if ultimo_processamento and os.path.exists(ultimo_processamento):
                abrir_painel_correcao_omr(ultimo_processamento)
            else:
                messagebox.showwarning(
                    "Correção OMR",
                    "A leitura foi concluída, mas a pasta do processamento não foi encontrada."
                )

        janela.after(0, finalizar_interface)

    except Exception as e:
        erro = str(e)

        def mostrar_erro():
            messagebox.showerror("Erro", erro)
            escrever_log(f"Erro: {erro}")
            definir_status("Erro na leitura OMR.")
            btn_omr.config(state="normal")

        janela.after(0, mostrar_erro)

# =========================
# INTERFACE
# =========================

janela = tk.Tk()
janela.title("OMRCheck")
janela.geometry("980x680")
janela.minsize(900, 620)
janela.configure(bg=COR_FUNDO)


style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Azul.Horizontal.TProgressbar",
    troughcolor="#E9EDF5",
    background=COR_AZUL,
    bordercolor=COR_BORDA,
    lightcolor=COR_AZUL,
    darkcolor=COR_AZUL,
    thickness=14
)

style.configure(
    "TFrame",
    background=COR_FUNDO
)

style.configure(
    "Card.TFrame",
    background=COR_CARD,
    relief="flat"
)

style.configure(
    "TLabel",
    background=COR_FUNDO,
    foreground=COR_TEXTO,
    font=("Segoe UI", 10)
)

style.configure(
    "Card.TLabel",
    background=COR_CARD,
    foreground=COR_TEXTO,
    font=("Segoe UI", 10)
)

style.configure(
    "Title.TLabel",
    background=COR_FUNDO,
    foreground=COR_TEXTO,
    font=("Segoe UI", 22, "bold")
)

style.configure(
    "Subtitle.TLabel",
    background=COR_FUNDO,
    foreground=COR_TEXTO_SUAVE,
    font=("Segoe UI", 11)
)

style.configure(
    "Primary.TButton",
    font=("Segoe UI", 10, "bold"),
    foreground="white",
    background=COR_AZUL,
    padding=(14, 10),
    borderwidth=0
)

style.map(
    "Primary.TButton",
    background=[
        ("active", COR_AZUL_ESCURO),
        ("pressed", COR_AZUL_ESCURO)
    ]
)

style.configure(
    "Secondary.TButton",
    font=("Segoe UI", 10),
    foreground=COR_TEXTO,
    background="#E9EDF5",
    padding=(12, 9),
    borderwidth=0
)

style.map(
    "Secondary.TButton",
    background=[
        ("active", "#DDE4F0"),
        ("pressed", "#DDE4F0")
    ]
)

style.configure(
    "Accent.TButton",
    font=("Segoe UI", 10, "bold"),
    foreground=COR_AZUL_ESCURO,
    background=COR_AMARELO,
    padding=(14, 10),
    borderwidth=0
)

style.map(
    "Accent.TButton",
    background=[
        ("active", "#E8BE14"),
        ("pressed", "#E8BE14")
    ]
)


container = ttk.Frame(janela, padding=24)
container.pack(fill=tk.BOTH, expand=True)


# Cabeçalho
header = ttk.Frame(container)
header.pack(fill=tk.X)

titulo = ttk.Label(
    header,
    text="OMRCheck",
    style="Title.TLabel"
)
titulo.pack(anchor="w")

subtitulo = ttk.Label(
    header,
    text="Leitura, conferência e geração de resultados de simulados.",
    style="Subtitle.TLabel"
)
subtitulo.pack(anchor="w", pady=(3, 18))


# Card da pasta
card_pasta = tk.Frame(
    container,
    bg=COR_CARD,
    highlightbackground=COR_BORDA,
    highlightthickness=1
)
card_pasta.pack(fill=tk.X, pady=(0, 16))

card_pasta_interno = tk.Frame(card_pasta, bg=COR_CARD)
card_pasta_interno.pack(fill=tk.X, padx=18, pady=16)

lbl_pasta = tk.Label(
    card_pasta_interno,
    text="Pasta do projeto",
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Segoe UI", 10, "bold")
)
lbl_pasta.pack(anchor="w")

linha_pasta = tk.Frame(card_pasta_interno, bg=COR_CARD)
linha_pasta.pack(fill=tk.X, pady=(8, 0))

entry_pasta = ttk.Entry(linha_pasta, font=("Segoe UI", 10))
entry_pasta.insert(0, pasta_projeto)
entry_pasta.configure(state="readonly")
entry_pasta.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

btn_pasta = ttk.Button(
    linha_pasta,
    text="Selecionar",
    command=escolher_pasta,
    style="Secondary.TButton"
)
btn_pasta.pack(side=tk.LEFT, padx=(10, 0))


# Card de ações
card_acoes = tk.Frame(
    container,
    bg=COR_CARD,
    highlightbackground=COR_BORDA,
    highlightthickness=1
)
card_acoes.pack(fill=tk.X, pady=(0, 16))

card_acoes_interno = tk.Frame(card_acoes, bg=COR_CARD)
card_acoes_interno.pack(fill=tk.X, padx=18, pady=18)

lbl_acoes = tk.Label(
    card_acoes_interno,
    text="Ações principais",
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Segoe UI", 12, "bold")
)
lbl_acoes.pack(anchor="w", pady=(0, 12))

grid_botoes = tk.Frame(card_acoes_interno, bg=COR_CARD)
grid_botoes.pack(fill=tk.X)

btn_omr = ttk.Button(
    grid_botoes,
    text="Selecionar imagens OMR",
    command=selecionar_imagens_omr,
    style="Primary.TButton"
)
btn_omr.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)

btn_base = ttk.Button(
    grid_botoes,
    text="Atualizar base de alunos",
    command=atualizar_base,
    style="Accent.TButton"
)
btn_base.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

btn_validacao = ttk.Button(
    grid_botoes,
    text="Painel de validação",
    command=abrir_painel_validacao,
    style="Secondary.TButton"
)
btn_validacao.grid(row=0, column=2, sticky="ew", padx=10, pady=5)

btn_saida = ttk.Button(
    grid_botoes,
    text="Abrir saída",
    command=abrir_saida,
    style="Secondary.TButton"
)
btn_saida.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5)

btn_ultimo = ttk.Button(
    grid_botoes,
    text="Abrir último processamento",
    command=abrir_ultimo_processamento,
    style="Secondary.TButton"
)
btn_ultimo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

for coluna in range(3):
    grid_botoes.columnconfigure(coluna, weight=1)


# Card de status/log
card_log = tk.Frame(
    container,
    bg=COR_CARD,
    highlightbackground=COR_BORDA,
    highlightthickness=1
)
card_log.pack(fill=tk.BOTH, expand=True)

card_log_interno = tk.Frame(card_log, bg=COR_CARD)
card_log_interno.pack(fill=tk.BOTH, expand=True, padx=18, pady=16)

linha_status = tk.Frame(card_log_interno, bg=COR_CARD)
linha_status.pack(fill=tk.X, pady=(0, 8))

lbl_log = tk.Label(
    linha_status,
    text="Log do processamento",
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Segoe UI", 12, "bold")
)
lbl_log.pack(side=tk.LEFT)

lbl_status = tk.Label(
    linha_status,
    text="Sistema iniciado.",
    bg=COR_CARD,
    fg=COR_TEXTO_SUAVE,
    font=("Segoe UI", 10)
)
lbl_status.pack(side=tk.RIGHT)

# Barra de progresso
frame_progresso = tk.Frame(card_log_interno, bg=COR_CARD)
frame_progresso.pack(fill=tk.X, pady=(0, 10))

progress_var = tk.IntVar(value=0)

barra_progresso = ttk.Progressbar(
    frame_progresso,
    orient="horizontal",
    mode="determinate",
    variable=progress_var,
    maximum=100,
    style="Azul.Horizontal.TProgressbar"
)
barra_progresso.pack(fill=tk.X)

lbl_progresso = tk.Label(
    frame_progresso,
    text="Aguardando processamento...",
    bg=COR_CARD,
    fg=COR_TEXTO_SUAVE,
    font=("Segoe UI", 9)
)
lbl_progresso.pack(anchor="w", pady=(4, 0))

frame_texto = tk.Frame(card_log_interno, bg=COR_CARD)
frame_texto.pack(fill=tk.BOTH, expand=True)

scroll_log = ttk.Scrollbar(frame_texto)
scroll_log.pack(side=tk.RIGHT, fill=tk.Y)

caixa_log = tk.Text(
    frame_texto,
    height=15,
    bg="#0F172A",
    fg="#E5E7EB",
    insertbackground="#E5E7EB",
    relief="flat",
    wrap="word",
    font=("Consolas", 10),
    yscrollcommand=scroll_log.set,
    padx=12,
    pady=10
)
caixa_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_log.config(command=caixa_log.yview)
caixa_log.configure(state="disabled")


# Rodapé
rodape = ttk.Label(
    container,
    text="Fluxo recomendado: Atualizar base → Selecionar imagens → Conferir no painel → Gerar CSV final.",
    style="Subtitle.TLabel"
)
rodape.pack(anchor="w", pady=(12, 0))


escrever_log("Sistema iniciado.")
escrever_log("1. Atualize a base de alunos, se necessário.")
escrever_log("2. Clique em Selecionar imagens OMR.")
escrever_log("3. Confira as marcações no painel.")
escrever_log("4. Gere o CSV final após a conferência.")

janela.mainloop()