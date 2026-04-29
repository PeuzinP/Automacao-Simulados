import os
import re
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

PASTA_ENTRADA = "entrada"
PASTA_SAIDA = "saida"
PASTA_PENDENCIAS = "pendencias"
PASTA_IMAGENS_FALHA = os.path.join(PASTA_PENDENCIAS, "imagens_ocr_falhou")

ARQUIVO_PENDENCIAS = os.path.join(PASTA_PENDENCIAS, "alunos_nao_identificados.csv")
ARQUIVO_SAIDA = os.path.join(PASTA_SAIDA, "respostas_corrigidas.csv")
ARQUIVO_CORRECOES = os.path.join(PASTA_PENDENCIAS, "correcoes_manuais.csv")


def encontrar_imagem(nome_arquivo):
    for pasta in [PASTA_ENTRADA, PASTA_IMAGENS_FALHA]:
        for ext in [".jpg", ".jpeg", ".png"]:
            caminho = os.path.join(pasta, nome_arquivo + ext)
            if os.path.exists(caminho):
                return caminho
    return None


class PainelValidacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Validação OCR")
        self.root.geometry("900x700")

        self.zoom = 0.25
        self.imagem_original = None
        self.imagem_tk = None
        self.indice = 0
        self.correcoes = []

        if not os.path.exists(ARQUIVO_PENDENCIAS):
            messagebox.showerror("Erro", "Arquivo de pendências não encontrado.")
            self.root.destroy()
            return

        if not os.path.exists(ARQUIVO_SAIDA):
            messagebox.showerror("Erro", "Arquivo de saída não encontrado.")
            self.root.destroy()
            return

        self.pendencias = pd.read_csv(ARQUIVO_PENDENCIAS, sep=";", encoding="utf-8-sig", dtype=str)
        self.saida = pd.read_csv(ARQUIVO_SAIDA, sep=";", encoding="utf-8-sig", dtype=str)

        self.criar_interface()
        self.carregar_pendencia()

    def criar_interface(self):
        self.titulo = tk.Label(
            self.root,
            text="Painel de Validação OCR",
            font=("Arial", 18, "bold")
        )
        self.titulo.pack(pady=10)

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.frame_principal = tk.Frame(self.canvas)

        self.frame_principal.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.janela_canvas = self.canvas.create_window(
            (0, 0),
            window=self.frame_principal,
            anchor="n"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        def ajustar_largura(event):
            self.canvas.itemconfig(self.janela_canvas, width=event.width)

        self.canvas.bind("<Configure>", ajustar_largura)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.label_imagem = tk.Label(self.frame_principal, text="Imagem do cartão")
        self.label_imagem.pack(pady=10)

        frame_zoom = tk.Frame(self.frame_principal)
        frame_zoom.pack(pady=5)

        tk.Button(frame_zoom, text="Zoom +", command=self.zoom_in).pack(side="left", padx=5)
        tk.Button(frame_zoom, text="Zoom -", command=self.zoom_out).pack(side="left", padx=5)

        self.info = tk.Label(
            self.frame_principal,
            text="",
            justify="left",
            font=("Arial", 11)
        )
        self.info.pack(pady=10)

        frame_input = tk.Frame(self.frame_principal)
        frame_input.pack(pady=10)

        tk.Label(frame_input, text="ID correto do aluno:").grid(row=0, column=0, padx=5)

        self.entry_id = tk.Entry(frame_input, width=25)
        self.entry_id.grid(row=0, column=1, padx=5)

        frame_botoes = tk.Frame(self.frame_principal)
        frame_botoes.pack(pady=15)

        tk.Button(
            frame_botoes,
            text="Confirmar Correção",
            bg="#2ca02c",
            fg="white",
            width=20,
            command=self.confirmar
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            frame_botoes,
            text="Pular",
            width=15,
            command=self.proximo
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            frame_botoes,
            text="Finalizar",
            width=15,
            command=self.finalizar
        ).grid(row=0, column=2, padx=5)

    def atualizar_imagem(self):
        if self.imagem_original is None:
            return

        largura, altura = self.imagem_original.size
        nova_largura = int(largura * self.zoom)
        nova_altura = int(altura * self.zoom)

        img = self.imagem_original.resize((nova_largura, nova_altura))
        self.imagem_tk = ImageTk.PhotoImage(img)

        self.label_imagem.config(image=self.imagem_tk, text="")

    def zoom_in(self):
        self.zoom *= 1.2
        self.zoom = min(self.zoom, 1.5)
        self.atualizar_imagem()

    def zoom_out(self):
        self.zoom /= 1.2
        self.zoom = max(self.zoom, 0.15)
        self.atualizar_imagem()

    def carregar_pendencia(self):
        if self.indice >= len(self.pendencias):
            self.finalizar()
            return

        linha = self.pendencias.iloc[self.indice]

        self.arquivo = str(linha.get("Arquivo", linha.iloc[0])).strip()
        motivo = str(linha.get("Motivo", "")).strip()
        id_ocr = str(linha.get("ID OCR", "")).strip()
        nome_ocr = str(linha.get("Nome OCR", "")).strip()
        confianca = str(linha.get("Confiança", "")).strip()
        metodo = str(linha.get("Método", "")).strip()

        texto = (
            f"Pendência {self.indice + 1} de {len(self.pendencias)}\n\n"
            f"Arquivo: {self.arquivo}\n"
            f"Motivo: {motivo}\n"
            f"ID OCR: {id_ocr}\n"
            f"Nome OCR: {nome_ocr}\n"
            f"Confiança: {confianca}\n"
            f"Método: {metodo}"
        )

        self.info.config(text=texto)
        self.entry_id.delete(0, tk.END)

        caminho_img = encontrar_imagem(self.arquivo)

        if caminho_img:
            self.imagem_original = Image.open(caminho_img)
            self.zoom = 0.25
            self.atualizar_imagem()
        else:
            self.label_imagem.config(image="", text="Imagem não encontrada")

    def confirmar(self):
        id_correto = self.entry_id.get().strip()

        if not id_correto:
            messagebox.showerror("Erro", "Digite o ID correto do aluno.")
            return

        coluna_nome = self.saida.columns[0]
        mascara = self.saida[coluna_nome].astype(str).str.strip() == self.arquivo

        if not mascara.any():
            messagebox.showerror("Erro", "Arquivo não encontrado no CSV de saída.")
            return

        novo_nome = re.sub(r"^\d+", id_correto, self.arquivo)
        self.saida.loc[mascara, coluna_nome] = novo_nome

        self.correcoes.append({
            "arquivo_original": self.arquivo,
            "arquivo_corrigido": novo_nome,
            "id_corrigido": id_correto
        })

        self.indice += 1
        self.carregar_pendencia()

    def proximo(self):
        self.indice += 1
        self.carregar_pendencia()

    def finalizar(self):
        self.saida.to_csv(ARQUIVO_SAIDA, index=False, sep=";", encoding="utf-8-sig")

        if self.correcoes:
            pd.DataFrame(self.correcoes).to_csv(
                ARQUIVO_CORRECOES,
                index=False,
                sep=";",
                encoding="utf-8-sig"
            )

        messagebox.showinfo("Finalizado", "Validação concluída e CSV atualizado.")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PainelValidacao(root)
    root.mainloop()