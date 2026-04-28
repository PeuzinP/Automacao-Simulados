import os
import re
import shutil
import pandas as pd
from PIL import Image
import pytesseract

# 🔥 CAMINHO DO TESSERACT (AJUSTE SE NECESSÁRIO)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PASTA_ENTRADA = "entrada"
PASTA_SAIDA = "saida"
PASTA_PENDENCIAS = "pendencias"
PASTA_IMAGENS_FALHA = os.path.join(PASTA_PENDENCIAS, "imagens_ocr_falhou")
BASE_ALUNOS = "base/alunos.csv"

os.makedirs(PASTA_SAIDA, exist_ok=True)
os.makedirs(PASTA_PENDENCIAS, exist_ok=True)
os.makedirs(PASTA_IMAGENS_FALHA, exist_ok=True)


def encontrar_csv():
    arquivos = [f for f in os.listdir(PASTA_ENTRADA) if f.endswith(".csv")]
    if not arquivos:
        raise FileNotFoundError("Nenhum CSV encontrado na pasta entrada.")
    return os.path.join(PASTA_ENTRADA, arquivos[0])


def encontrar_imagem(nome):
    for ext in [".jpg", ".jpeg", ".png"]:
        caminho = os.path.join(PASTA_ENTRADA, nome + ext)
        if os.path.exists(caminho):
            return caminho
    return None


def extrair_info_imagem(caminho):
    imagem = Image.open(caminho)

    largura, altura = imagem.size
    topo = imagem.crop((0, 0, largura, int(altura * 0.28)))

    texto = pytesseract.image_to_string(topo, lang="por")

    match = re.search(r"\[(\d+)\]\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ ]+)", texto.upper())

    if match:
        return match.group(1), match.group(2).strip(), texto

    return None, None, texto


def carregar_base():
    base = pd.read_csv(BASE_ALUNOS, sep=";", encoding="utf-8-sig", dtype=str)
    base.columns = base.columns.str.strip()

    base["ID"] = base["ID"].astype(str).str.strip()
    base["ALUNO"] = base["ALUNO"].astype(str).str.upper().str.strip()

    return base


def buscar_aluno(base, id_extraido, nome_extraido):
    if id_extraido:
        res = base[base["ID"] == id_extraido]
        if len(res) == 1:
            return res.iloc[0]

    if nome_extraido:
        res = base[base["ALUNO"] == nome_extraido]
        if len(res) == 1:
            return res.iloc[0]

    return None


def corrigir_textos(df):
    df = df.replace("InglÃªs", "Ingles", regex=True)
    df = df.replace("Inglês", "Ingles", regex=True)
    return df


def trocar_colunas(df):
    coluna_codigo = "group006.Código de Barras/QRCode001"
    coluna_pergunta = "group006.Pergunta006"

    colunas = df.columns.tolist()

    if coluna_codigo not in colunas or coluna_pergunta not in colunas:
        print("ERRO: colunas G/H não encontradas.")
        print(colunas)
        return df

    idx_codigo = colunas.index(coluna_codigo)
    idx_pergunta = colunas.index(coluna_pergunta)

    print("ANTES:")
    print("Código está na posição:", idx_codigo)
    print("Pergunta está na posição:", idx_pergunta)

    # Só troca se Código estiver antes de Pergunta
    if idx_codigo < idx_pergunta:
        colunas[idx_codigo], colunas[idx_pergunta] = colunas[idx_pergunta], colunas[idx_codigo]
        df = df[colunas]
        print("Troca feita.")
    else:
        print("Arquivo já estava com G/H corrigido. Não troquei novamente.")

    print("DEPOIS:")
    print("Coluna G:", df.columns[6])
    print("Coluna H:", df.columns[7])

    return df


def main():
    print("🚀 Iniciando processamento...")

    csv_path = encontrar_csv()
    print("📄 CSV encontrado:", csv_path)

    base = carregar_base()
    print("📚 Base carregada:", len(base), "alunos")

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig", dtype=str)
    df.columns = df.columns.str.strip()

    df = corrigir_textos(df)
    df = trocar_colunas(df)

    pendencias = []
    coluna_nome = df.columns[0]

    for index, row in df.iterrows():
        nome_arquivo = str(row[coluna_nome]).strip()

        if "_037" in nome_arquivo or nome_arquivo.endswith("_"):

            imagem = encontrar_imagem(nome_arquivo)

            if not imagem:
                pendencias.append([nome_arquivo, "Imagem não encontrada", "", ""])
                continue

            try:
                id_extraido, nome_extraido, texto = extrair_info_imagem(imagem)

                aluno = buscar_aluno(base, id_extraido, nome_extraido)

                if aluno is not None:
                    id_correto = str(aluno["ID"])

                    novo_nome = re.sub(r"^\d+", id_correto, nome_arquivo)
                    df.at[index, coluna_nome] = novo_nome

                    print(f"✅ Corrigido: {nome_arquivo} → {novo_nome}")

                else:
                    pendencias.append([
                        nome_arquivo,
                        "Aluno não encontrado",
                        id_extraido or "",
                        nome_extraido or ""
                    ])

                    shutil.copy(imagem, os.path.join(PASTA_IMAGENS_FALHA, os.path.basename(imagem)))

            except Exception as e:
                pendencias.append([nome_arquivo, "Erro OCR", "", str(e)])

                shutil.copy(imagem, os.path.join(PASTA_IMAGENS_FALHA, os.path.basename(imagem)))

    saida = os.path.join(PASTA_SAIDA, "respostas_corrigidas.csv")
    df.to_csv(saida, index=False, sep=";", encoding="utf-8-sig")

    print("📁 Arquivo final:", saida)

    if pendencias:
        pend_path = os.path.join(PASTA_PENDENCIAS, "alunos_nao_identificados.csv")

        pd.DataFrame(
            pendencias,
            columns=["Arquivo", "Motivo", "ID OCR", "Nome OCR"]
        ).to_csv(pend_path, index=False, sep=";", encoding="utf-8-sig")

        print("⚠️ Pendências:", len(pendencias))
    else:
        print("✅ Nenhuma pendência encontrada!")


if __name__ == "__main__":
    main()