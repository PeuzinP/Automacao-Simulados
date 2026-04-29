import os
import cv2
import pandas as pd
import numpy as np

EXTENSOES_IMAGEM = [".jpg", ".jpeg", ".png"]


def listar_imagens(pasta_imagens):
    return [
        arquivo for arquivo in os.listdir(pasta_imagens)
        if arquivo.lower().endswith(tuple(EXTENSOES_IMAGEM))
    ]


def gerar_imagem_conferencia(caminho_imagem, pasta_debug):
    os.makedirs(pasta_debug, exist_ok=True)

    dados = np.fromfile(caminho_imagem, dtype=np.uint8)
    imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR)

    if imagem is None:
        return None, "Não foi possível abrir a imagem"

    altura, largura = imagem.shape[:2]

    # Marcações visuais só para conferência
    cv2.rectangle(imagem, (10, 10), (largura - 10, altura - 10), (0, 255, 0), 4)

    # Área aproximada onde ficam as respostas
    y_inicio = int(altura * 0.665)
    y_fim = int(altura * 0.93)
    x_inicio = int(largura * 0.02)
    x_fim = int(largura * 0.98)

    cv2.rectangle(imagem, (x_inicio, y_inicio), (x_fim, y_fim), (0, 0, 255), 4)

    nome_saida = os.path.basename(caminho_imagem)
    caminho_saida = os.path.join(pasta_debug, nome_saida)

    cv2.imwrite(caminho_saida, imagem)

    return caminho_saida, "Imagem de conferência gerada"


def processar_imagens_omr(pasta_imagens, pasta_saida="saida"):
    os.makedirs(pasta_saida, exist_ok=True)

    pasta_debug = os.path.join(pasta_saida, "debug_omr")
    imagens = listar_imagens(pasta_imagens)

    log = []

    for imagem in imagens:
        caminho_imagem = os.path.join(pasta_imagens, imagem)

        caminho_debug, detalhe = gerar_imagem_conferencia(caminho_imagem, pasta_debug)
        resultado_bolhas, detalhe_bolhas = detectar_bolhas_area_respostas(
        caminho_imagem,
        pasta_debug
)

        status = "OK" if caminho_debug else "ERRO"

        log.append({
            "arquivo": imagem,
            "status": status,
            "detalhe": detalhe,
            "debug": caminho_debug or "",
            "total_respostas_lidas": resultado_bolhas["total_respostas_lidas"] if resultado_bolhas else 0,
            "total_erros": resultado_bolhas["total_erros"] if resultado_bolhas else 0,
            "erros": " | ".join(resultado_bolhas["erros"]) if resultado_bolhas else "",
            "debug_bolhas": resultado_bolhas["debug_bolhas"] if resultado_bolhas else "",
            "detalhe_bolhas": detalhe_bolhas
        })

    caminho_log = os.path.join(pasta_saida, "log_leitura_omr.csv")

    pd.DataFrame(log).to_csv(
        caminho_log,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    return {
        "total_imagens": len(imagens),
        "log": caminho_log,
        "debug": pasta_debug
    }
    
def detectar_bolhas_area_respostas(caminho_imagem, pasta_debug):
    os.makedirs(pasta_debug, exist_ok=True)

    dados = np.fromfile(caminho_imagem, dtype=np.uint8)
    imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR)

    if imagem is None:
        return None, "Não foi possível abrir a imagem"

    altura, largura = imagem.shape[:2]

    y_inicio = int(altura * 0.665)
    y_fim = int(altura * 0.93)
    x_inicio = int(largura * 0.02)
    x_fim = int(largura * 0.98)

    area = imagem[y_inicio:y_fim, x_inicio:x_fim]
    cinza = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        cinza,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    h, w = area.shape[:2]

    alternativas = ["A", "B", "C", "D", "E"]
    respostas = {}
    erros = []

    total_blocos = 6
    questoes_por_bloco = 15

    block_w = w / total_blocos

    # posições relativas das bolhas dentro de cada bloco
    x_rel = [0.24, 0.41, 0.58, 0.75, 0.91]

    margem_topo = int(h * 0.08)
    margem_baixo = int(h * 0.03)
    area_util_y = h - margem_topo - margem_baixo
    passo_y = area_util_y / questoes_por_bloco

    raio = 12
    limite_marcacao = 0.35

    for bloco in range(total_blocos):
        questao_inicial = 91 + bloco * 15

        for linha in range(questoes_por_bloco):
            questao = questao_inicial + linha

            y_centro = int(margem_topo + linha * passo_y + passo_y / 2)

            scores = []

            for alt_index, rel in enumerate(x_rel):
                x_centro = int(bloco * block_w + block_w * rel)

                recorte = thresh[
                    y_centro - raio:y_centro + raio,
                    x_centro - raio:x_centro + raio
                ]

                preenchimento = cv2.countNonZero(recorte) / (recorte.shape[0] * recorte.shape[1])
                scores.append(preenchimento)

                cor = (0, 0, 255)

                if preenchimento >= limite_marcacao:
                    cor = (0, 255, 0)

                cv2.rectangle(
                    area,
                    (x_centro - raio, y_centro - raio),
                    (x_centro + raio, y_centro + raio),
                    cor,
                    2
                )

            marcadas = [
                alternativas[i]
                for i, score in enumerate(scores)
                if score >= limite_marcacao
            ]

            if len(marcadas) == 1:
                respostas[f"Pergunta{questao:03d}"] = marcadas[0]
            elif len(marcadas) == 0:
                respostas[f"Pergunta{questao:03d}"] = ""
                erros.append(f"Pergunta{questao:03d}: vazia")
            else:
                respostas[f"Pergunta{questao:03d}"] = "/".join(marcadas)
                erros.append(f"Pergunta{questao:03d}: dupla marcação")

    caminho_saida = os.path.join(
        pasta_debug,
        "grade_" + os.path.basename(caminho_imagem)
    )

    cv2.imwrite(caminho_saida, area)

    return {
        "total_respostas_lidas": len(respostas),
        "total_erros": len(erros),
        "respostas": respostas,
        "erros": erros,
        "debug_bolhas": caminho_saida
    }, "Leitura por grade concluída"