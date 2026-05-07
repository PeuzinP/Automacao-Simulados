import os
import json
import math
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class PainelCorrecaoOMR:
    def __init__(self, root, pasta_manual="saida/manual_omr"):
        self.root = root
        self.root.title("Correção Manual OMR")

        self.pasta_manual = pasta_manual
        self.arquivos_json = self.listar_jsons()
        self.indice_atual = 0

        self.dados = None
        self.imagem_original = None
        self.imagem_tk = None

        self.escala = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.raio_bolha = 10

        self.criar_interface()

        if not self.arquivos_json:
            messagebox.showinfo(
                "Correção Manual OMR",
                "Nenhuma pendência manual encontrada em saida/manual_omr."
            )
        else:
            self.carregar_pendencia_atual()

    def listar_jsons(self):
        if not os.path.exists(self.pasta_manual):
            return []

        return sorted([
            arquivo for arquivo in os.listdir(self.pasta_manual)
            if arquivo.lower().endswith(".json")
        ])

    def criar_interface(self):
        topo = tk.Frame(self.root)
        topo.pack(fill="x", padx=10, pady=8)

        self.label_status = tk.Label(
            topo,
            text="Correção Manual OMR",
            font=("Arial", 14, "bold")
        )
        self.label_status.pack(side="left")

        botoes = tk.Frame(topo)
        botoes.pack(side="right")

        tk.Button(
            botoes,
            text="Anterior",
            command=self.anterior
        ).pack(side="left", padx=3)

        tk.Button(
            botoes,
            text="Próximo",
            command=self.proximo
        ).pack(side="left", padx=3)

        tk.Button(
            botoes,
            text="Salvar",
            command=self.salvar
        ).pack(side="left", padx=3)

        tk.Button(
            botoes,
            text="Recarregar",
            command=self.recarregar
        ).pack(side="left", padx=3)

        corpo = tk.Frame(self.root)
        corpo.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(corpo, bg="#eeeeee")
        self.canvas.pack(side="left", fill="both", expand=True)

        barra_y = tk.Scrollbar(corpo, orient="vertical", command=self.canvas.yview)
        barra_y.pack(side="right", fill="y")

        barra_x = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        barra_x.pack(side="bottom", fill="x")

        self.canvas.configure(
            yscrollcommand=barra_y.set,
            xscrollcommand=barra_x.set
        )

        rodape = tk.Frame(self.root)
        rodape.pack(fill="x", padx=10, pady=6)

        self.label_info = tk.Label(
            rodape,
            text="Clique esquerdo: marcar | Clique direito: remover | Salvar ao finalizar",
            font=("Arial", 10)
        )
        self.label_info.pack(side="left")

        self.label_arquivo = tk.Label(
            rodape,
            text="",
            font=("Arial", 10, "bold")
        )
        self.label_arquivo.pack(side="right")

        self.canvas.bind("<Button-1>", self.clique_esquerdo)
        self.canvas.bind("<Button-3>", self.clique_direito)

    def carregar_pendencia_atual(self):
        if not self.arquivos_json:
            return

        arquivo_json = self.arquivos_json[self.indice_atual]
        caminho_json = os.path.join(self.pasta_manual, arquivo_json)

        with open(caminho_json, "r", encoding="utf-8") as f:
            self.dados = json.load(f)

        caminho_imagem = self.dados.get("caminho_imagem")

        if not caminho_imagem or not os.path.exists(caminho_imagem):
            messagebox.showerror(
                "Erro",
                f"Imagem não encontrada:\n{caminho_imagem}"
            )
            return

        self.imagem_original = Image.open(caminho_imagem).convert("RGB")

        self.ajustar_imagem_para_tela()
        self.desenhar()

        total = len(self.arquivos_json)
        self.label_status.config(
            text=f"Pendência {self.indice_atual + 1} de {total}"
        )

        self.label_arquivo.config(
            text=arquivo_json
        )

    def ajustar_imagem_para_tela(self):
        largura, altura = self.imagem_original.size

        largura_max = 1100
        altura_max = 850

        escala_x = largura_max / largura
        escala_y = altura_max / altura

        self.escala = min(escala_x, escala_y, 1.0)

    def desenhar(self):
        self.canvas.delete("all")

        if self.imagem_original is None or self.dados is None:
            return

        largura, altura = self.imagem_original.size

        largura_view = int(largura * self.escala)
        altura_view = int(altura * self.escala)

        imagem_redimensionada = self.imagem_original.resize(
            (largura_view, altura_view),
            Image.LANCZOS
        )

        self.imagem_tk = ImageTk.PhotoImage(imagem_redimensionada)

        self.canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.imagem_tk
        )

        self.canvas.configure(
            scrollregion=(0, 0, largura_view, altura_view)
        )

        self.desenhar_bolhas()
        self.desenhar_respostas()

    def desenhar_bolhas(self):
        pontos = self.dados.get("pontos_mapeados", {})

        for pergunta, alternativas in pontos.items():
            for alternativa, coord in alternativas.items():
                x = coord["x"] * self.escala
                y = coord["y"] * self.escala

                r = self.raio_bolha * self.escala

                self.canvas.create_oval(
                    x - r,
                    y - r,
                    x + r,
                    y + r,
                    outline="red",
                    width=2
                )

                self.canvas.create_text(
                    x,
                    y,
                    text=alternativa,
                    fill="red",
                    font=("Arial", 7, "bold")
                )

    def desenhar_respostas(self):
        respostas = self.dados.get("respostas", {})
        pontos = self.dados.get("pontos_mapeados", {})

        for pergunta, resposta in respostas.items():
            if not pergunta.startswith("Pergunta"):
                continue

            if not resposta:
                continue

            if pergunta not in pontos:
                continue

            if resposta not in pontos[pergunta]:
                continue

            coord = pontos[pergunta][resposta]

            x = coord["x"] * self.escala
            y = coord["y"] * self.escala

            r = (self.raio_bolha + 4) * self.escala

            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                outline="green",
                width=3
            )

            self.canvas.create_text(
                x,
                y - 16,
                text=f"{pergunta}:{resposta}",
                fill="green",
                font=("Arial", 8, "bold")
            )

    def converter_clique_para_imagem(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        x_img = canvas_x / self.escala
        y_img = canvas_y / self.escala

        return x_img, y_img

    def encontrar_bolha_mais_proxima(self, x_img, y_img):
        pontos = self.dados.get("pontos_mapeados", {})

        menor_distancia = None
        melhor = None

        for pergunta, alternativas in pontos.items():
            for alternativa, coord in alternativas.items():
                dx = coord["x"] - x_img
                dy = coord["y"] - y_img
                distancia = math.sqrt(dx * dx + dy * dy)

                if menor_distancia is None or distancia < menor_distancia:
                    menor_distancia = distancia
                    melhor = {
                        "pergunta": pergunta,
                        "alternativa": alternativa,
                        "distancia": distancia
                    }

        limite_clique = 28

        if melhor and melhor["distancia"] <= limite_clique:
            return melhor

        return None

    def clique_esquerdo(self, event):
        if self.dados is None:
            return

        x_img, y_img = self.converter_clique_para_imagem(event)
        bolha = self.encontrar_bolha_mais_proxima(x_img, y_img)

        if not bolha:
            return

        pergunta = bolha["pergunta"]
        alternativa = bolha["alternativa"]

        self.dados.setdefault("respostas", {})
        self.dados["respostas"][pergunta] = alternativa

        self.remover_erro_da_pergunta(pergunta)

        self.desenhar()

    def clique_direito(self, event):
        if self.dados is None:
            return

        x_img, y_img = self.converter_clique_para_imagem(event)
        bolha = self.encontrar_bolha_mais_proxima(x_img, y_img)

        if not bolha:
            return

        pergunta = bolha["pergunta"]

        self.dados.setdefault("respostas", {})
        self.dados["respostas"][pergunta] = ""

        self.adicionar_erro_da_pergunta(pergunta, "removida manualmente")

        self.desenhar()

    def remover_erro_da_pergunta(self, pergunta):
        erros = self.dados.get("erros", [])

        erros_filtrados = [
            erro for erro in erros
            if not erro.startswith(pergunta + ":")
        ]

        self.dados["erros"] = erros_filtrados

    def adicionar_erro_da_pergunta(self, pergunta, motivo):
        self.remover_erro_da_pergunta(pergunta)

        self.dados.setdefault("erros", [])
        self.dados["erros"].append(f"{pergunta}: {motivo}")

    def salvar(self):
        if self.dados is None:
            return

        arquivo_json = self.arquivos_json[self.indice_atual]
        caminho_json = os.path.join(self.pasta_manual, arquivo_json)

        self.dados["corrigido_manualmente"] = True

        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=4)

        messagebox.showinfo(
            "Salvo",
            "Correção manual salva com sucesso."
        )

    def proximo(self):
        if not self.arquivos_json:
            return

        self.indice_atual += 1

        if self.indice_atual >= len(self.arquivos_json):
            self.indice_atual = 0

        self.carregar_pendencia_atual()

    def anterior(self):
        if not self.arquivos_json:
            return

        self.indice_atual -= 1

        if self.indice_atual < 0:
            self.indice_atual = len(self.arquivos_json) - 1

        self.carregar_pendencia_atual()

    def recarregar(self):
        self.arquivos_json = self.listar_jsons()
        self.indice_atual = 0
        self.carregar_pendencia_atual()


def abrir_painel_correcao():
    root = tk.Tk()
    root.geometry("1200x900")
    app = PainelCorrecaoOMR(root)
    root.mainloop()


if __name__ == "__main__":
    abrir_painel_correcao()