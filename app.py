import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading


pasta_projeto = os.getcwd()


def escolher_pasta():
    global pasta_projeto

    pasta = filedialog.askdirectory()
    if pasta:
        pasta_projeto = pasta
        entry_pasta.delete(0, tk.END)
        entry_pasta.insert(0, pasta)


def escrever_log(texto):
    caixa_log.insert(tk.END, texto + "\n")
    caixa_log.see(tk.END)
    janela.update_idletasks()


def executar_comando(comando):
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
        else:
            escrever_log("Processo finalizado com erro.")

    except Exception as e:
        escrever_log(f"Erro: {e}")


def atualizar_base():
    caixa_log.delete("1.0", tk.END)
    escrever_log("Atualizando base de alunos...")

    thread = threading.Thread(
        target=executar_comando,
        args=("python atualizar_base.py",)
    )
    thread.start()


def processar_simulado():
    caixa_log.delete("1.0", tk.END)

    entrada = os.path.join(pasta_projeto, "entrada")
    base = os.path.join(pasta_projeto, "base", "alunos.csv")

    if not os.path.exists(entrada):
        messagebox.showerror("Erro", "A pasta entrada não foi encontrada.")
        return

    if not os.path.exists(base):
        messagebox.showerror("Erro", "A base de alunos não foi encontrada. Atualize a base primeiro.")
        return

    escrever_log("Processando simulado...")

    thread = threading.Thread(
        target=executar_comando,
        args=("python main.py",)
    )
    thread.start()


def abrir_saida():
    caminho = os.path.join(pasta_projeto, "saida")

    if os.path.exists(caminho):
        os.startfile(caminho)
    else:
        messagebox.showerror("Erro", "Pasta saida não encontrada.")


def abrir_pendencias():
    caminho = os.path.join(pasta_projeto, "pendencias")

    if os.path.exists(caminho):
        os.startfile(caminho)
    else:
        messagebox.showerror("Erro", "Pasta pendencias não encontrada.")


janela = tk.Tk()
janela.title("Automação de Simulados")
janela.geometry("700x500")

titulo = tk.Label(
    janela,
    text="Automação de Simulados",
    font=("Arial", 16, "bold")
)
titulo.pack(pady=10)

frame_pasta = tk.Frame(janela)
frame_pasta.pack(pady=5)

tk.Label(frame_pasta, text="Pasta do projeto:").pack(anchor="w")

entry_pasta = tk.Entry(frame_pasta, width=80)
entry_pasta.insert(0, pasta_projeto)
entry_pasta.pack(side=tk.LEFT, padx=5)

tk.Button(
    frame_pasta,
    text="Selecionar",
    command=escolher_pasta
).pack(side=tk.LEFT)

frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=15)

tk.Button(
    frame_botoes,
    text="Atualizar Base",
    command=atualizar_base,
    width=18,
    bg="#1f77b4",
    fg="white"
).grid(row=0, column=0, padx=5)

tk.Button(
    frame_botoes,
    text="Processar Simulado",
    command=processar_simulado,
    width=18,
    bg="#2ca02c",
    fg="white"
).grid(row=0, column=1, padx=5)

tk.Button(
    frame_botoes,
    text="Abrir Saída",
    command=abrir_saida,
    width=18
).grid(row=0, column=2, padx=5)

tk.Button(
    frame_botoes,
    text="Abrir Pendências",
    command=abrir_pendencias,
    width=18
).grid(row=0, column=3, padx=5)

tk.Label(janela, text="Log do processamento:").pack(anchor="w", padx=20)

caixa_log = tk.Text(janela, height=18, width=85)
caixa_log.pack(padx=20, pady=10)

escrever_log("Sistema iniciado.")
escrever_log("1. Atualize a base.")
escrever_log("2. Coloque o CSV e as imagens na pasta entrada.")
escrever_log("3. Clique em Processar Simulado.")

janela.mainloop()