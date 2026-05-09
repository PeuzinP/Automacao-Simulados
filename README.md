# OMRCheck

Sistema interno para leitura de cartões-resposta OMR, conferência manual das marcações e geração do CSV final no padrão esperado para importação dos resultados dos simulados.

O projeto foi desenvolvido para automatizar o fluxo de leitura de cartões-resposta escaneados, reduzindo retrabalho manual e aumentando a segurança na conferência das respostas.

---

## Visão geral

O sistema permite:

- Atualizar a base de alunos;
- Ler imagens de cartões-resposta OMR;
- Identificar RA preenchido no cartão;
- Ler ou montar o código de barras com base no RA e no ID do aluno;
- Gerar imagens de debug com as marcações detectadas;
- Abrir um painel de correção manual;
- Corrigir marcações com clique manual;
- Gerar o CSV final somente após conferência;
- Organizar cada processamento em uma pasta própria dentro de `saida`.

---

## Fluxo recomendado

1. Abrir o aplicativo.
2. Atualizar a base de alunos, se necessário.
3. Clicar em **Selecionar imagens OMR**.
4. Escolher a pasta com as imagens escaneadas dos cartões.
5. Aguardar a leitura automática.
6. Conferir as marcações no **Painel de Correção OMR**.
7. Corrigir manualmente as marcações, se necessário.
8. Clicar em **Gerar CSV Final**.
9. Usar o arquivo `respostas_omr.csv` gerado na pasta do processamento.

---

## Estrutura do projeto

```text
Automação Simulados/
│
├── app.py
├── omr_reader.py
├── painel_correcao_omr.py
├── painel_validacao.py
├── atualizar_base.py
├── config.py
├── requirements.txt
├── README.md
│
├── templates/
│   └── modelo_cartao.xtmpl
│
├── base/
│   └── alunos.csv
│
├── entrada/
│
├── saida/
│
└── _backup_antigos/

# OMRCheck

Sistema interno para leitura de cartões-resposta OMR, conferência manual das marcações e geração do CSV final no padrão esperado para importação dos resultados dos simulados.

O projeto foi desenvolvido para automatizar o fluxo de leitura de cartões-resposta escaneados, reduzindo retrabalho manual e aumentando a segurança na conferência das respostas.

---

## Visão geral

O sistema permite:

- Atualizar a base de alunos;
- Ler imagens de cartões-resposta OMR;
- Identificar RA preenchido no cartão;
- Ler ou montar o código de barras com base no RA e no ID do aluno;
- Gerar imagens de debug com as marcações detectadas;
- Abrir um painel de correção manual;
- Corrigir marcações com clique manual;
- Gerar o CSV final somente após conferência;
- Organizar cada processamento em uma pasta própria dentro de `saida`.

---

## Fluxo recomendado

1. Abrir o aplicativo.
2. Atualizar a base de alunos, se necessário.
3. Clicar em **Selecionar imagens OMR**.
4. Escolher a pasta com as imagens escaneadas dos cartões.
5. Aguardar a leitura automática.
6. Conferir as marcações no **Painel de Correção OMR**.
7. Corrigir manualmente as marcações, se necessário.
8. Clicar em **Gerar CSV Final**.
9. Usar o arquivo `respostas_omr.csv` gerado na pasta do processamento.

---

## Estrutura do projeto

```text
Automação Simulados/
│
├── app.py
├── omr_reader.py
├── painel_correcao_omr.py
├── painel_validacao.py
├── atualizar_base.py
├── config.py
├── requirements.txt
├── README.md
│
├── templates/
│   └── modelo_cartao.xtmpl
│
├── base/
│   └── alunos.csv
│
├── entrada/
│
├── saida/
│
└── _backup_antigos/
```

---

## Principais arquivos

### `app.py`

Arquivo principal do sistema.

Responsável por abrir a interface inicial, onde é possível:

- Atualizar a base de alunos;
- Selecionar imagens OMR;
- Abrir o painel de validação;
- Abrir a pasta de saída;
- Abrir o último processamento;
- Acompanhar o log do processamento.

Para iniciar o sistema pelo terminal:

```powershell
python app.py
```

---

### `omr_reader.py`

Responsável pela leitura dos cartões OMR.

Principais funções:

- Ler imagens da pasta selecionada;
- Carregar o modelo `.xtmpl` do FormScanner;
- Detectar os cantos do cartão;
- Mapear as bolhas com base no template;
- Ler RA, idioma, cor da capa e respostas;
- Ler ou montar o código de barras;
- Gerar imagens de debug;
- Gerar `leituras_omr.json`;
- Gerar logs do processamento;
- Organizar cada execução em uma pasta própria.

Importante: o CSV final não é gerado diretamente nesse arquivo. Ele é gerado somente após a conferência manual no painel.

---

### `painel_correcao_omr.py`

Painel usado para conferir e corrigir manualmente as marcações OMR.

Recursos disponíveis:

- Visualização das imagens processadas;
- Marcação manual com clique;
- Escolha entre marcação verde e vermelha;
- Zoom em diferentes níveis;
- Adaptação da imagem à largura;
- Adaptação da imagem à janela;
- Navegação entre imagens;
- Salvamento das correções;
- Geração do CSV final.

Regras de correção:

```text
Verde = adicionar ou confirmar uma resposta
Vermelho = remover/anular uma resposta
Botão direito = remover uma marcação manual
```

Exemplo:

Se o OMR marcou uma alternativa indevidamente e a questão deveria estar em branco, selecione **Vermelho**, clique sobre a bolha marcada e depois clique em **Gerar CSV Final**.

---

### `atualizar_base.py`

Arquivo responsável por atualizar a base de alunos usada no cruzamento entre RA e ID.

A base deve conter, no mínimo, as colunas:

```text
RA
ID
```

O sistema usa o RA lido no cartão para localizar o ID do aluno e montar o código no formato:

```text
codigoDaProvaAID
```

Exemplo:

```text
12479A10425
```

---

### `painel_validacao.py`

Painel auxiliar para validações manuais relacionadas ao fluxo de conferência e validação de dados.

---

### `config.py`

Arquivo reservado para configurações do projeto.

Pode concentrar caminhos, URLs, nomes de arquivos e parâmetros usados pelo sistema.

---

### `requirements.txt`

Arquivo com as bibliotecas necessárias para executar o projeto.

Para instalar as dependências:

```powershell
pip install -r requirements.txt
```

---

## Pastas importantes

### `templates/`

Contém o modelo `.xtmpl` exportado do FormScanner.

Arquivo esperado:

```text
templates/modelo_cartao.xtmpl
```

Esse arquivo é essencial para o sistema saber onde estão os campos do cartão.

Sem esse arquivo, a leitura OMR não funcionará corretamente.

---

### `base/`

Contém a base de alunos.

Exemplo:

```text
base/alunos.csv
```

A base precisa conter os campos de RA e ID.

Essa base é usada para localizar o ID do aluno a partir do RA preenchido no cartão.

---

### `entrada/`

Pasta opcional para armazenar arquivos de entrada.

No fluxo atual, as imagens podem ser selecionadas diretamente pela interface, então não é obrigatório usar essa pasta.

---

### `saida/`

Pasta onde cada processamento é salvo.

A cada leitura OMR, o sistema cria uma pasta como:

```text
saida/processamento_20260508_151556/
```

Dentro dela ficam os arquivos e pastas do processamento.

---

### `_backup_antigos/`

Pasta usada para guardar arquivos antigos ou versões anteriores do projeto.

Exemplos de arquivos que podem ficar nessa pasta:

```text
main.py
main.spec
teste_ocr.py
painel_correcao.py
```

Esses arquivos não fazem parte do fluxo principal atual, mas podem ser mantidos como histórico.

---

## Estrutura de um processamento

Após executar uma leitura OMR, o sistema cria uma pasta parecida com esta:

```text
saida/
└── processamento_20260508_151556/
    ├── debug_omr/
    │   ├── template_imagem_001.jpg
    │   ├── template_imagem_002.jpg
    │   └── ...
    │
    ├── manual_omr/
    │   ├── correcoes_omr.json
    │   └── imagens_corrigidas/
    │
    ├── pendencias/
    │
    ├── log_leitura_omr.csv
    ├── resumo_processamento.txt
    ├── leituras_omr.json
    └── respostas_omr.csv
```

O arquivo `respostas_omr.csv` só aparece depois de clicar em **Gerar CSV Final** no painel de correção.

---

## Arquivos gerados

### `leituras_omr.json`

Arquivo interno usado pelo painel de correção.

Ele armazena:

- Nome da imagem;
- Respostas lidas automaticamente;
- Pontos mapeados de cada bolha;
- RA lido;
- Código de barras;
- Erros encontrados;
- Caminhos das imagens de debug.

Esse arquivo é essencial para que o painel saiba qual bolha corresponde a qual pergunta e alternativa.

Sem esse arquivo, o painel não consegue gerar o CSV final.

---

### `correcoes_omr.json`

Arquivo gerado pelo painel de correção.

Armazena as correções manuais feitas pelo usuário.

As correções são aplicadas sobre a leitura automática antes da geração do CSV final.

---

### `respostas_omr.csv`

CSV final gerado após a conferência manual.

Esse é o arquivo que deve ser usado para importação dos resultados.

O CSV é gerado somente após o clique em:

```text
Gerar CSV Final
```

---

### `log_leitura_omr.csv`

Arquivo de log com o status de cada imagem processada.

Inclui:

- Nome do arquivo;
- Status;
- RA;
- Código de barras;
- Quantidade de erros;
- Se foi enviada para correção manual;
- Caminho dos arquivos de debug;
- Detalhes do processamento.

---

### `resumo_processamento.txt`

Resumo geral da execução.

Inclui:

- Data e hora;
- Pasta de imagens;
- Modelo utilizado;
- Total de imagens;
- Total com leitura OK;
- Total com erro;
- Total enviado para correção manual;
- Arquivos gerados.

---

## Como instalar dependências

Com o Python instalado, rode:

```powershell
pip install -r requirements.txt
```

Caso ainda não exista um `requirements.txt`, instale manualmente:

```powershell
pip install opencv-python pandas numpy pillow pyzbar openpyxl
```

Dependências principais:

- `opencv-python`
- `pandas`
- `numpy`
- `pillow`
- `pyzbar`
- `openpyxl`

---

## Como executar pelo terminal

Dentro da pasta do projeto, rode:

```powershell
python app.py
```

O sistema abrirá a interface principal.

---

## Como usar o sistema

### 1. Abrir o app

Execute:

```powershell
python app.py
```

Ou abra o executável, caso já tenha sido gerado.

---

### 2. Atualizar a base de alunos

Clique em:

```text
Atualizar base de alunos
```

Esse processo atualiza a base usada para cruzar RA e ID.

---

### 3. Selecionar imagens OMR

Clique em:

```text
Selecionar imagens OMR
```

Depois selecione a pasta onde estão as imagens escaneadas dos cartões-resposta.

---

### 4. Conferir as marcações

Após a leitura, o painel de correção será aberto automaticamente.

Nele é possível:

- Navegar entre imagens;
- Conferir marcações detectadas;
- Corrigir marcações incorretas;
- Ajustar o zoom;
- Salvar marcações;
- Gerar o CSV final.

---

### 5. Corrigir manualmente

No painel:

```text
Verde = adicionar ou confirmar resposta
Vermelho = remover ou anular resposta
Botão direito = remover marcação manual
```

---

### 6. Gerar CSV Final

Depois de conferir as imagens, clique em:

```text
Gerar CSV Final
```

O sistema criará o arquivo:

```text
respostas_omr.csv
```

dentro da pasta do processamento.

---

## Como gerar executável

Para transformar o app em um programa clicável no Windows, use o PyInstaller.

Instale:

```powershell
pip install pyinstaller
```

Gere o executável:

```powershell
pyinstaller --onedir --windowed --name AutomacaoSimulados app.py
```

O executável será criado em:

```text
dist/AutomacaoSimulados/AutomacaoSimulados.exe
```

---

## Estrutura recomendada para o executável

Dentro da pasta `dist/AutomacaoSimulados/`, mantenha também:

```text
templates/
base/
entrada/
saida/
```

Principalmente:

```text
templates/modelo_cartao.xtmpl
```

Sem esse arquivo, a leitura OMR não funcionará.

A estrutura recomendada é:

```text
dist/
└── AutomacaoSimulados/
    ├── AutomacaoSimulados.exe
    ├── templates/
    │   └── modelo_cartao.xtmpl
    ├── base/
    │   └── alunos.csv
    ├── entrada/
    └── saida/
```

---

## Como criar atalho na Área de Trabalho

1. Acesse a pasta:

```text
dist/AutomacaoSimulados/
```

2. Clique com o botão direito em:

```text
AutomacaoSimulados.exe
```

3. Selecione:

```text
Enviar para > Área de trabalho criar atalho
```

Assim o sistema ficará clicável pela Área de Trabalho, como outros programas do Windows.

---

## Observações importantes

- O sistema não gera o CSV final imediatamente após a leitura.
- O CSV final só é criado após a conferência manual.
- Sempre use o botão **Gerar CSV Final** no painel de correção.
- A pasta `templates/` precisa conter o modelo `.xtmpl`.
- A base de alunos precisa conter RA e ID.
- Cada processamento fica isolado em uma pasta própria dentro de `saida`.
- O arquivo `leituras_omr.json` é obrigatório para o painel gerar o CSV final.
- Caso o painel informe que `leituras_omr.json` não foi encontrado, rode novamente a leitura OMR.

---

## Fluxo final do sistema

```text
Atualizar base
↓
Selecionar imagens OMR
↓
Sistema lê os cartões
↓
Sistema gera debug e leituras_omr.json
↓
Painel de correção é aberto
↓
Usuário confere e corrige
↓
Usuário clica em Gerar CSV Final
↓
Sistema gera respostas_omr.csv
```

---

## Status atual

O sistema atualmente contempla:

- Leitura automática de cartões OMR;
- Identificação de RA;
- Complementação do código de barras com base no RA e ID;
- Geração de imagens de debug;
- Painel de conferência manual;
- Correção manual com marcações verdes e vermelhas;
- Zoom e centralização da imagem;
- Geração do CSV final após validação;
- Organização de cada processamento em pasta própria;
- Interface principal com botões de ação;
- Painel de correção com visual mais apresentável.

---

## Próximas melhorias possíveis

Algumas melhorias futuras possíveis:

- Criar instalador `.exe`;
- Adicionar ícone personalizado ao executável;
- Adicionar tela de carregamento;
- Adicionar barra de progresso real na leitura OMR;
- Permitir seleção direta do modelo `.xtmpl`;
- Permitir seleção direta da base de alunos;
- Criar relatório final em PDF;
- Adicionar autenticação de usuário;
- Gerar backup automático dos CSVs finais;
- Melhorar a leitura de cartões com baixa qualidade de escaneamento.

---

## Nome do projeto

```text
Automação de Simulados
```

Aplicação interna para automação, leitura, conferência e geração de resultados de simulados.