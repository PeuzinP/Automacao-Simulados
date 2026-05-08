import os
import json
import csv
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

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
COR_VERDE = "#16A34A"
COR_VERMELHO = "#DC2626"
COR_BORDA = "#D9DEE8"
COR_CANVAS = "#E9EDF5"

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS


class PainelCorrecaoOMR:
    def __init__(self, pasta_processamento):
        self.pasta_processamento = pasta_processamento

        self.pasta_debug = os.path.join(pasta_processamento, "debug_omr")
        self.pasta_manual = os.path.join(pasta_processamento, "manual_omr")
        self.pasta_corrigidas = os.path.join(self.pasta_manual, "imagens_corrigidas")

        os.makedirs(self.pasta_manual, exist_ok=True)
        os.makedirs(self.pasta_corrigidas, exist_ok=True)

        self.caminho_json_correcoes = os.path.join(
            self.pasta_manual,
            "correcoes_omr.json"
        )

        self.caminho_json_leituras = os.path.join(
            self.pasta_processamento,
            "leituras_omr.json"
        )

        self.caminho_csv_final = os.path.join(
            self.pasta_processamento,
            "respostas_omr.csv"
        )

        self.leituras_omr = self.carregar_leituras_omr()
        self.correcoes = self.carregar_correcoes()

        self.imagens = self.listar_imagens_debug()
        self.indice_atual = 0

        self.modo_cor = "verde"

        self.zoom_modo = "Adaptar à janela"
        self.zoom_atual = 1.0

        self.imagem_original = None
        self.imagem_renderizada = None
        self.photo = None

        self.offset_x = 0
        self.offset_y = 0

        self.root = tk.Toplevel()
        self.root.title("Painel de Correção OMR")
        self.root.geometry("1500x900")
        self.root.minsize(1200, 760)
        self.root.configure(bg=COR_FUNDO)

        self.criar_interface()

        if not self.imagens:
            messagebox.showinfo(
                "Correção Manual OMR",
                "Nenhuma imagem de debug encontrada em debug_omr."
            )
            self.root.destroy()
            return

        self.carregar_imagem_atual()

    def carregar_leituras_omr(self):
        if not os.path.exists(self.caminho_json_leituras):
            return {}

        try:
            with open(self.caminho_json_leituras, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def carregar_correcoes(self):
        if not os.path.exists(self.caminho_json_correcoes):
            return {}

        try:
            with open(self.caminho_json_correcoes, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def salvar_correcoes_json(self):
        with open(self.caminho_json_correcoes, "w", encoding="utf-8") as f:
            json.dump(self.correcoes, f, ensure_ascii=False, indent=4)

    def listar_imagens_debug(self):
        if not os.path.exists(self.pasta_debug):
            return []

        extensoes = (".jpg", ".jpeg", ".png", ".bmp")

        imagens = []

        for nome in os.listdir(self.pasta_debug):
            nome_lower = nome.lower()

            if nome_lower.startswith("template_") and nome_lower.endswith(extensoes):
                imagens.append(nome)

        imagens.sort()
        return imagens

    def criar_interface(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Painel.TFrame",
            background=COR_FUNDO
        )

        style.configure(
            "Card.TFrame",
            background=COR_CARD
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            foreground="white",
            background=COR_AZUL,
            padding=(14, 9),
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
            padding=(12, 8),
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
            "Danger.TButton",
            font=("Segoe UI", 10, "bold"),
            foreground="white",
            background=COR_VERMELHO,
            padding=(12, 8),
            borderwidth=0
        )

        style.map(
            "Danger.TButton",
            background=[
                ("active", "#B91C1C"),
                ("pressed", "#B91C1C")
            ]
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            foreground=COR_AZUL_ESCURO,
            background=COR_AMARELO,
            padding=(14, 9),
            borderwidth=0
        )

        style.map(
            "Accent.TButton",
            background=[
                ("active", "#E8BE14"),
                ("pressed", "#E8BE14")
            ]
        )

        style.configure(
            "Zoom.TCombobox",
            font=("Segoe UI", 10),
            padding=4
        )

        # =========================
        # CONTAINER PRINCIPAL
        # =========================

        container = tk.Frame(self.root, bg=COR_FUNDO)
        container.pack(fill=tk.BOTH, expand=True, padx=18, pady=16)

        # =========================
        # CABEÇALHO
        # =========================

        header = tk.Frame(container, bg=COR_FUNDO)
        header.pack(fill=tk.X, pady=(0, 12))

        bloco_titulo = tk.Frame(header, bg=COR_FUNDO)
        bloco_titulo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        titulo = tk.Label(
            bloco_titulo,
            text="Painel de Correção OMR",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 20, "bold")
        )
        titulo.pack(anchor="w")

        subtitulo = tk.Label(
            bloco_titulo,
            text="Confira as marcações, ajuste manualmente e gere o CSV final somente após a validação.",
            bg=COR_FUNDO,
            fg=COR_TEXTO_SUAVE,
            font=("Segoe UI", 10)
        )
        subtitulo.pack(anchor="w", pady=(2, 0))

        # =========================
        # BARRA SUPERIOR DE CONTROLES
        # =========================

        barra = tk.Frame(
            container,
            bg=COR_CARD,
            highlightbackground=COR_BORDA,
            highlightthickness=1
        )
        barra.pack(fill=tk.X, pady=(0, 12))

        barra_interna = tk.Frame(barra, bg=COR_CARD)
        barra_interna.pack(fill=tk.X, padx=14, pady=10)

        # Bloco de marcação
        bloco_marcacao = tk.Frame(barra_interna, bg=COR_CARD)
        bloco_marcacao.pack(side=tk.LEFT)

        tk.Label(
            bloco_marcacao,
            text="Tipo de marcação",
            bg=COR_CARD,
            fg=COR_TEXTO,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        linha_radios = tk.Frame(bloco_marcacao, bg=COR_CARD)
        linha_radios.pack(anchor="w", pady=(4, 0))

        self.var_cor = tk.StringVar(value="verde")

        radio_verde = tk.Radiobutton(
            linha_radios,
            text="Verde",
            variable=self.var_cor,
            value="verde",
            command=self.alterar_cor,
            bg=COR_CARD,
            fg=COR_TEXTO,
            selectcolor=COR_CARD,
            activebackground=COR_CARD,
            font=("Segoe UI", 10)
        )
        radio_verde.pack(side=tk.LEFT, padx=(0, 10))

        radio_vermelho = tk.Radiobutton(
            linha_radios,
            text="Vermelho",
            variable=self.var_cor,
            value="vermelho",
            command=self.alterar_cor,
            bg=COR_CARD,
            fg=COR_TEXTO,
            selectcolor=COR_CARD,
            activebackground=COR_CARD,
            font=("Segoe UI", 10)
        )
        radio_vermelho.pack(side=tk.LEFT)

        # Separador visual
        separador_1 = tk.Frame(barra_interna, bg=COR_BORDA, width=1, height=42)
        separador_1.pack(side=tk.LEFT, padx=18)

        # Bloco de navegação
        bloco_nav = tk.Frame(barra_interna, bg=COR_CARD)
        bloco_nav.pack(side=tk.LEFT)

        tk.Label(
            bloco_nav,
            text="Navegação",
            bg=COR_CARD,
            fg=COR_TEXTO,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        linha_nav = tk.Frame(bloco_nav, bg=COR_CARD)
        linha_nav.pack(anchor="w", pady=(4, 0))

        ttk.Button(
            linha_nav,
            text="← Anterior",
            command=self.imagem_anterior,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(
            linha_nav,
            text="Próximo →",
            command=self.proxima_imagem,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT)

        # Separador visual
        separador_2 = tk.Frame(barra_interna, bg=COR_BORDA, width=1, height=42)
        separador_2.pack(side=tk.LEFT, padx=18)

        # Bloco de zoom
        bloco_zoom = tk.Frame(barra_interna, bg=COR_CARD)
        bloco_zoom.pack(side=tk.LEFT)

        tk.Label(
            bloco_zoom,
            text="Visualização",
            bg=COR_CARD,
            fg=COR_TEXTO,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        linha_zoom = tk.Frame(bloco_zoom, bg=COR_CARD)
        linha_zoom.pack(anchor="w", pady=(4, 0))

        tk.Label(
            linha_zoom,
            text="Zoom:",
            bg=COR_CARD,
            fg=COR_TEXTO_SUAVE,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.var_zoom = tk.StringVar(value="Adaptar à janela")

        self.combo_zoom = ttk.Combobox(
            linha_zoom,
            textvariable=self.var_zoom,
            state="readonly",
            width=18,
            values=[
                "50%",
                "75%",
                "100%",
                "125%",
                "150%",
                "200%",
                "Adaptar à largura",
                "Adaptar à janela"
            ],
            style="Zoom.TCombobox"
        )
        self.combo_zoom.pack(side=tk.LEFT)
        self.combo_zoom.bind("<<ComboboxSelected>>", self.alterar_zoom)

        # Botão principal à direita
        bloco_final = tk.Frame(barra_interna, bg=COR_CARD)
        bloco_final.pack(side=tk.RIGHT)

        ttk.Button(
            bloco_final,
            text="Gerar CSV Final",
            command=self.salvar,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            bloco_final,
            text="Salvar marcações",
            command=self.salvar_marcacoes_sem_csv,
            style="Accent.TButton"
        ).pack(side=tk.LEFT)

        # =========================
        # INFORMAÇÕES DA IMAGEM
        # =========================

        info_card = tk.Frame(
            container,
            bg=COR_CARD,
            highlightbackground=COR_BORDA,
            highlightthickness=1
        )
        info_card.pack(fill=tk.X, pady=(0, 12))

        info_interno = tk.Frame(info_card, bg=COR_CARD)
        info_interno.pack(fill=tk.X, padx=14, pady=8)

        self.lbl_info = tk.Label(
            info_interno,
            text="",
            anchor="w",
            bg=COR_CARD,
            fg=COR_TEXTO,
            font=("Segoe UI", 10)
        )
        self.lbl_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        legenda = tk.Label(
            info_interno,
            text="Clique esquerdo adiciona | Botão direito remove",
            anchor="e",
            bg=COR_CARD,
            fg=COR_TEXTO_SUAVE,
            font=("Segoe UI", 9)
        )
        legenda.pack(side=tk.RIGHT)

        # =========================
        # ÁREA DA IMAGEM
        # =========================

        frame_canvas_externo = tk.Frame(
            container,
            bg=COR_CARD,
            highlightbackground=COR_BORDA,
            highlightthickness=1
        )
        frame_canvas_externo.pack(fill=tk.BOTH, expand=True)

        frame_canvas = tk.Frame(frame_canvas_externo, bg=COR_CARD)
        frame_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(
            frame_canvas,
            bg=COR_CANVAS,
            highlightthickness=0
        )

        self.scroll_y = ttk.Scrollbar(
            frame_canvas,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )

        self.scroll_x = ttk.Scrollbar(
            frame_canvas,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )

        self.canvas.configure(
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )

        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.adicionar_marcacao)
        self.canvas.bind("<Button-3>", self.remover_marcacao)
        self.canvas.bind("<Configure>", self.ao_redimensionar_canvas)

    def alterar_cor(self):
        self.modo_cor = self.var_cor.get()
        self.atualizar_info()

    def nome_imagem_atual(self):
        if not self.imagens:
            return None

        return self.imagens[self.indice_atual]

    def caminho_imagem_atual(self):
        nome = self.nome_imagem_atual()
        return os.path.join(self.pasta_debug, nome)

    def carregar_imagem_atual(self):
        caminho = self.caminho_imagem_atual()

        self.imagem_original = Image.open(caminho).convert("RGB")

        nome = self.nome_imagem_atual()

        if nome not in self.correcoes:
            self.correcoes[nome] = []

        self.aplicar_zoom_modo()
        self.redesenhar_imagem()

    def ao_redimensionar_canvas(self, event=None):
        if self.imagem_original is not None:
            self.aplicar_zoom_modo()
            self.redesenhar_imagem()

    def alterar_zoom(self, event=None):
        self.zoom_modo = self.var_zoom.get()
        self.aplicar_zoom_modo()
        self.redesenhar_imagem()

    def aplicar_zoom_modo(self):
        if self.imagem_original is None:
            return

        largura_canvas = max(self.canvas.winfo_width(), 1)
        altura_canvas = max(self.canvas.winfo_height(), 1)

        largura_img, altura_img = self.imagem_original.size

        modo = self.var_zoom.get()

        if modo.endswith("%"):
            self.zoom_atual = int(modo.replace("%", "")) / 100.0

        elif modo == "Adaptar à largura":
            self.zoom_atual = largura_canvas / largura_img

        elif modo == "Adaptar à janela":
            self.zoom_atual = min(
                largura_canvas / largura_img,
                altura_canvas / altura_img
            )

        self.zoom_atual = max(0.1, min(self.zoom_atual, 5.0))

    def redesenhar_imagem(self):
        if self.imagem_original is None:
            return

        imagem = self.imagem_original.copy()
        draw = ImageDraw.Draw(imagem)

        nome = self.nome_imagem_atual()
        correcoes_img = self.correcoes.get(nome, [])

        for correcao in correcoes_img:
            x = correcao["x"]
            y = correcao["y"]
            cor_nome = correcao.get("cor", "verde")
            pergunta = correcao.get("pergunta", "")
            alternativa = correcao.get("alternativa", "")

            if cor_nome == "verde":
                cor = (0, 255, 0)
            else:
                cor = (255, 0, 0)

            raio = 15

            draw.ellipse(
                (x - raio, y - raio, x + raio, y + raio),
                outline=cor,
                width=4
            )

            draw.ellipse(
                (x - 4, y - 4, x + 4, y + 4),
                fill=cor
            )

            if pergunta and alternativa:
                texto = f"{pergunta}:{alternativa}"
                draw.text((x + 8, y - 18), texto, fill=cor)

        largura_original, altura_original = imagem.size

        nova_largura = int(largura_original * self.zoom_atual)
        nova_altura = int(altura_original * self.zoom_atual)

        imagem_zoom = imagem.resize(
            (nova_largura, nova_altura),
            RESAMPLE
        )

        self.imagem_renderizada = imagem_zoom
        self.photo = ImageTk.PhotoImage(imagem_zoom)

        self.canvas.delete("all")

        largura_canvas = max(self.canvas.winfo_width(), 1)
        altura_canvas = max(self.canvas.winfo_height(), 1)

        self.offset_x = max((largura_canvas - nova_largura) // 2, 0)
        self.offset_y = max((altura_canvas - nova_altura) // 2, 0)

        self.canvas.create_image(
            self.offset_x,
            self.offset_y,
            image=self.photo,
            anchor="nw"
        )

        scroll_largura = max(nova_largura + self.offset_x * 2, largura_canvas)
        scroll_altura = max(nova_altura + self.offset_y * 2, altura_canvas)

        self.canvas.configure(
            scrollregion=(0, 0, scroll_largura, scroll_altura)
        )

        self.atualizar_info()

    def atualizar_info(self):
        nome = self.nome_imagem_atual()
        total = len(self.imagens)
        atual = self.indice_atual + 1
        qtd = len(self.correcoes.get(nome, []))

        self.lbl_info.config(
            text=(
                f"Imagem {atual}/{total}   |   "
                f"{nome}   |   "
                f"Marcações manuais: {qtd}   |   "
                f"Modo atual: {self.var_cor.get().capitalize()}"
            )
        )

    def coordenada_real_canvas(self, event):
        x_canvas = self.canvas.canvasx(event.x)
        y_canvas = self.canvas.canvasy(event.y)

        x_real = int((x_canvas - self.offset_x) / self.zoom_atual)
        y_real = int((y_canvas - self.offset_y) / self.zoom_atual)

        return x_real, y_real

    def obter_dados_leitura_imagem(self, nome_imagem):
        if nome_imagem in self.leituras_omr:
            return self.leituras_omr[nome_imagem]

        nome_sem_template = nome_imagem.replace("template_", "", 1)

        if nome_sem_template in self.leituras_omr:
            return self.leituras_omr[nome_sem_template]

        for chave, valor in self.leituras_omr.items():
            if self.normalizar_nome(chave) == self.normalizar_nome(nome_imagem):
                return valor

        return {}

    def localizar_ponto_mais_proximo(self, x, y):
        nome = self.nome_imagem_atual()
        dados = self.obter_dados_leitura_imagem(nome)

        pontos_mapeados = dados.get("pontos_mapeados", {})

        melhor = None
        menor_distancia = 999999

        for pergunta, alternativas in pontos_mapeados.items():
            for alternativa, ponto in alternativas.items():
                px = ponto.get("x")
                py = ponto.get("y")

                if px is None or py is None:
                    continue

                dx = float(px) - x
                dy = float(py) - y
                dist = (dx ** 2 + dy ** 2) ** 0.5

                if dist < menor_distancia:
                    menor_distancia = dist
                    melhor = {
                        "pergunta": pergunta,
                        "alternativa": alternativa,
                        "x": int(round(float(px))),
                        "y": int(round(float(py))),
                        "distancia": dist
                    }

        if melhor and melhor["distancia"] <= 22:
            return melhor

        return None

    def adicionar_marcacao(self, event):
        nome = self.nome_imagem_atual()

        x, y = self.coordenada_real_canvas(event)

        if x < 0 or y < 0:
            return

        ponto = self.localizar_ponto_mais_proximo(x, y)

        if ponto:
            x = ponto["x"]
            y = ponto["y"]
            pergunta = ponto["pergunta"]
            alternativa = ponto["alternativa"]
        else:
            pergunta = ""
            alternativa = ""

        cor = self.var_cor.get()

        nova = {
            "x": int(x),
            "y": int(y),
            "cor": cor,
            "pergunta": pergunta,
            "alternativa": alternativa
        }

        self.correcoes[nome].append(nova)
        self.redesenhar_imagem()

    def remover_marcacao(self, event):
        nome = self.nome_imagem_atual()

        x, y = self.coordenada_real_canvas(event)

        lista = self.correcoes.get(nome, [])

        if not lista:
            return

        menor_distancia = 999999
        indice_remover = None

        for i, item in enumerate(lista):
            dx = item["x"] - x
            dy = item["y"] - y
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < menor_distancia:
                menor_distancia = dist
                indice_remover = i

        if indice_remover is not None and menor_distancia <= 28:
            lista.pop(indice_remover)

        self.redesenhar_imagem()

    def salvar_imagem_corrigida(self):
        if self.imagem_original is None:
            return

        nome = self.nome_imagem_atual()

        imagem = self.imagem_original.copy()
        draw = ImageDraw.Draw(imagem)

        for correcao in self.correcoes.get(nome, []):
            x = correcao["x"]
            y = correcao["y"]
            cor_nome = correcao.get("cor", "verde")

            if cor_nome == "verde":
                cor = (0, 255, 0)
            else:
                cor = (255, 0, 0)

            raio = 15

            draw.ellipse(
                (x - raio, y - raio, x + raio, y + raio),
                outline=cor,
                width=4
            )

            draw.ellipse(
                (x - 4, y - 4, x + 4, y + 4),
                fill=cor
            )

        caminho_saida = os.path.join(
            self.pasta_corrigidas,
            nome
        )

        imagem.save(caminho_saida)

    def salvar_marcacoes_sem_csv(self):
        self.salvar_correcoes_json()
        self.salvar_imagem_corrigida()

        messagebox.showinfo(
            "Marcações salvas",
            "As marcações manuais foram salvas com sucesso."
        )

    def salvar(self):
        self.salvar_correcoes_json()
        self.salvar_imagem_corrigida()

        caminho_csv = self.gerar_csv_final()

        if caminho_csv:
            messagebox.showinfo(
                "Correção Manual OMR",
                f"Correções salvas com sucesso.\nCSV final gerado em:\n{caminho_csv}"
            )
        else:
            messagebox.showwarning(
                "Correção Manual OMR",
                "Correções salvas, mas não foi possível gerar o CSV final."
            )
    

    def proxima_imagem(self):
        self.salvar_correcoes_json()
        self.salvar_imagem_corrigida()

        if self.indice_atual < len(self.imagens) - 1:
            self.indice_atual += 1
            self.carregar_imagem_atual()

    def imagem_anterior(self):
        self.salvar_correcoes_json()
        self.salvar_imagem_corrigida()

        if self.indice_atual > 0:
            self.indice_atual -= 1
            self.carregar_imagem_atual()

    def normalizar_nome(self, nome):
        nome = os.path.basename(str(nome))
        nome = nome.replace("template_", "", 1)

        nome_sem_ext, _ = os.path.splitext(nome)

        return nome_sem_ext.strip().lower()

    def localizar_csv_original(self):
        candidatos = []

        for nome in os.listdir(self.pasta_processamento):
            nome_lower = nome.lower()

            if nome_lower.endswith(".csv") and "corrigido" not in nome_lower:
                candidatos.append(nome)

        prioridade = []

        for nome in candidatos:
            nome_lower = nome.lower()

            if "respostas" in nome_lower or "resultado" in nome_lower:
                prioridade.append(nome)

        if prioridade:
            return os.path.join(self.pasta_processamento, prioridade[0])

        if candidatos:
            return os.path.join(self.pasta_processamento, candidatos[0])

        return None

    def detectar_dialeto_csv(self, caminho_csv):
        with open(caminho_csv, "r", encoding="utf-8-sig", newline="") as f:
            amostra = f.read(4096)

        try:
            dialect = csv.Sniffer().sniff(amostra, delimiters=";,")
            return dialect.delimiter
        except Exception:
            return ";"

    def indice_coluna_por_pergunta(self, pergunta):
        """
        Mapeamento baseado no CSV padrão do FormScanner:

        Coluna 0 = Nome do arquivo
        Pergunta001 a Pergunta006 = RA, colunas 1 a 6
        Coluna 7 = Código de Barras/QRCode001
        Pergunta007 = idioma, coluna 8
        Pergunta008 = cor da capa, coluna 9
        Pergunta009 em diante = respostas, coluna pergunta + 1
        """

        if not pergunta.startswith("Pergunta"):
            return None

        try:
            numero = int(pergunta.replace("Pergunta", ""))
        except Exception:
            return None

        if 1 <= numero <= 6:
            return numero

        if numero == 7:
            return 8

        if numero >= 8:
            return numero + 1

        return None

    def aplicar_correcoes_em_respostas(self, nome_imagem, respostas_automaticas):
        respostas_finais = dict(respostas_automaticas)

        correcoes_img = self.correcoes.get(nome_imagem, [])

        for correcao in correcoes_img:
            pergunta = correcao.get("pergunta")
            alternativa = correcao.get("alternativa")
            cor = correcao.get("cor")

            if not pergunta or not alternativa:
                continue

            if cor == "vermelho":
                if respostas_finais.get(pergunta) == alternativa:
                    respostas_finais[pergunta] = ""

            elif cor == "verde":
                respostas_finais[pergunta] = alternativa

        return respostas_finais

    def gerar_csv_corrigido(self):
        caminho_csv_original = self.localizar_csv_original()

        if not caminho_csv_original:
            return None

        try:
            delimitador = self.detectar_dialeto_csv(caminho_csv_original)

            with open(caminho_csv_original, "r", encoding="utf-8-sig", newline="") as f:
                leitor = list(csv.reader(f, delimiter=delimitador))

            if not leitor:
                return None

            cabecalho = leitor[0]
            linhas = leitor[1:]

            mapa_linhas = {}

            for idx, linha in enumerate(linhas):
                if not linha:
                    continue

                nome_arquivo = linha[0]
                chave = self.normalizar_nome(nome_arquivo)

                mapa_linhas[chave] = idx

            for nome_imagem in self.imagens:
                dados = self.obter_dados_leitura_imagem(nome_imagem)

                respostas_auto = dados.get("respostas", {})
                respostas_finais = self.aplicar_correcoes_em_respostas(
                    nome_imagem,
                    respostas_auto
                )

                arquivo_original = dados.get("arquivo_original", nome_imagem)

                chave = self.normalizar_nome(arquivo_original)

                if chave not in mapa_linhas:
                    chave = self.normalizar_nome(nome_imagem)

                if chave not in mapa_linhas:
                    continue

                idx_linha = mapa_linhas[chave]
                linha = linhas[idx_linha]

                for pergunta, resposta in respostas_finais.items():
                    indice_coluna = self.indice_coluna_por_pergunta(pergunta)

                    if indice_coluna is None:
                        continue

                    while len(linha) <= indice_coluna:
                        linha.append("")

                    linha[indice_coluna] = resposta

                codigo = respostas_finais.get("Codigo de Barras/QRCode001", "")

                if codigo:
                    while len(linha) <= 7:
                        linha.append("")

                    linha[7] = codigo

                linhas[idx_linha] = linha

            with open(self.caminho_csv_corrigido, "w", encoding="utf-8-sig", newline="") as f:
                escritor = csv.writer(f, delimiter=delimitador)
                escritor.writerow(cabecalho)
                escritor.writerows(linhas)

            return self.caminho_csv_corrigido

        except Exception as e:
            messagebox.showerror(
                "Erro ao gerar CSV corrigido",
                str(e)
            )
            return None

    def ordenar_chaves_pergunta(self, chaves):
        def extrair_numero(chave):
            import re
            match = re.search(r"(\d+)$", str(chave))
            return int(match.group(1)) if match else 999999

        return sorted(chaves, key=extrair_numero)


    def aplicar_correcoes_em_respostas(self, nome_imagem, respostas_automaticas):
        respostas_finais = dict(respostas_automaticas)

        correcoes_img = self.correcoes.get(nome_imagem, [])

        for correcao in correcoes_img:
            pergunta = correcao.get("pergunta")
            alternativa = correcao.get("alternativa")
            cor = correcao.get("cor")

            if not pergunta or not alternativa:
                continue

            if cor == "vermelho":
                if respostas_finais.get(pergunta) == alternativa:
                    respostas_finais[pergunta] = ""

            elif cor == "verde":
                respostas_finais[pergunta] = alternativa

        return respostas_finais


    def gerar_csv_final(self):
        if not self.leituras_omr:
            messagebox.showwarning(
                "CSV Final",
                "Arquivo leituras_omr.json não encontrado ou vazio."
            )
            return None

        try:
            todas_perguntas = set()

            for nome_imagem, dados in self.leituras_omr.items():
                respostas = dados.get("respostas", {})
                todas_perguntas.update(respostas.keys())

            perguntas_ordenadas = self.ordenar_chaves_pergunta(todas_perguntas)

            perguntas_objetivas = []

            for pergunta in perguntas_ordenadas:
                import re
                match = re.search(r"(\d+)$", pergunta)

                if not match:
                    continue

                numero = int(match.group(1))

                if numero >= 9:
                    perguntas_objetivas.append(pergunta)

            cabecalho = [
                "Nome do arquivo",
                "group001",
                "group002",
                "group003",
                "group004",
                "group005",
                "group006",
                "Código de Barras/QRCode001",
                "group008",
                "group009",
            ] + (["group010"] * len(perguntas_objetivas))

            linhas = []

            for nome_imagem in self.imagens:
                dados = self.obter_dados_leitura_imagem(nome_imagem)

                if not dados:
                    continue

                respostas_auto = dados.get("respostas", {})

                respostas_finais = self.aplicar_correcoes_em_respostas(
                    nome_imagem,
                    respostas_auto
                )

                arquivo_original = dados.get("arquivo_original", nome_imagem)
                nome_arquivo = os.path.splitext(os.path.basename(arquivo_original))[0]

                registro_academico = str(
                    dados.get("registro_academico", "")
                ).strip()

                if not registro_academico:
                    partes_ra = []

                    for i in range(1, 7):
                        chave = f"Pergunta{i:03d}"
                        partes_ra.append(str(respostas_finais.get(chave, "")).strip())

                    registro_academico = "".join(partes_ra)

                import re
                registro_academico = re.sub(r"[^A-Za-z0-9]", "", registro_academico)

                ra_digitos = list(registro_academico[:6])

                while len(ra_digitos) < 6:
                    ra_digitos.append("")

                codigo_barras = str(
                    respostas_finais.get("Codigo de Barras/QRCode001", "")
                ).strip()

                if not codigo_barras:
                    codigo_barras = str(
                        respostas_finais.get("Código de Barras/QRCode001", "")
                    ).strip()

                if not codigo_barras:
                    codigo_barras = str(
                        dados.get("codigo_barras", "")
                    ).strip()

                idioma = respostas_finais.get("Pergunta007", "")
                cor_capa = respostas_finais.get("Pergunta008", "")

                linha = [
                    nome_arquivo,
                    ra_digitos[0],
                    ra_digitos[1],
                    ra_digitos[2],
                    ra_digitos[3],
                    ra_digitos[4],
                    ra_digitos[5],
                    codigo_barras,
                    idioma,
                    cor_capa,
                ]

                for pergunta in perguntas_objetivas:
                    linha.append(respostas_finais.get(pergunta, ""))

                linhas.append(linha)

            with open(self.caminho_csv_final, "w", encoding="utf-8-sig", newline="") as f:
                escritor = csv.writer(f, delimiter=";")
                escritor.writerow(cabecalho)
                escritor.writerows(linhas)

            return self.caminho_csv_final

        except Exception as e:
            messagebox.showerror(
                "Erro ao gerar CSV final",
                str(e)
            )
            return None

def abrir_painel_correcao_omr(pasta_processamento):
    PainelCorrecaoOMR(pasta_processamento)


def abrir_painel_correcao(pasta_processamento):
    PainelCorrecaoOMR(pasta_processamento)