# Codificador-Bi

`Codificador-Bi` é um projeto que explora a representação de dados de forma binária, visual e sonora. Ele é composto por duas aplicações com interface gráfica (GUI):

1.  **Codificador (`codificador.py`)**: Converte uma mensagem de texto em um formato visual que representa os bits da mensagem.
2.  **Interpretador (`intrepletador.py`)**: Lê o arquivo codificado, decodifica a mensagem, a exibe, e é capaz de "tocar" os bits como um sinal de áudio.

## Sobre o Projeto

A ideia central é demonstrar como qualquer informação digital, no fundo, é uma sequência de zeros e uns. O projeto torna esse conceito abstrato em algo tangível e interativo.

- O **Codificador** pega um texto simples (como "Olá Mundo") e o transforma em uma representação visual usando caracteres especiais (`█` para 1 e ` ` para 0), salvando o resultado em um arquivo de texto.
- O **Interpretador** faz o caminho inverso: lê esse arquivo, reconstrói a mensagem original e ainda oferece uma forma de "ouvir" a sequência de bits, associando um som ao bit '1' e silêncio ao bit '0'.

## Funcionalidades

### Codificador

- **Entrada de Texto**: Uma área para digitar ou colar a mensagem a ser codificada.
- **Preview em Tempo Real**: Mostra como a mensagem está sendo convertida para o formato binário visual.
- **Estatísticas**: Exibe o número de bits e bytes aproximados da mensagem.
- **Salvar Arquivo**: Salva a mensagem codificada em um arquivo `.txt`.
- **Gerador de QR Code**: Cria um QR Code a partir da mensagem original.
- **Copiar para Área de Transferência**: Copia o conteúdo codificado.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/32407743-14ce-4f7b-b81e-962a739826fc" />


### Interpretador

- **Carregar Arquivo**: Abre e processa um arquivo `.txt` gerado pelo codificador.
- **Visualização de Bits**: Exibe a sequência de bits de forma clara.
- **Decodificação de Texto**: Mostra a mensagem original decodificada.
- **Player de Áudio**: Toca a sequência de bits como um sinal de áudio.
    - A frequência do som e a duração de cada bit são customizáveis.
    - Durante a reprodução, o bit que está sendo tocado é destacado na interface.
- **Gerador de QR Code**: Cria um QR Code a partir da mensagem decodificada.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/09dee565-9ffb-47c0-ba13-6063dd7b186a" />


## Como Funciona

### Processo de Codificação

1.  **Texto para Bytes**: A mensagem de texto é primeiro convertida para uma sequência de bytes usando a codificação `UTF-8`.
2.  **Bytes para Bits**: Cada byte é transformado em sua representação binária de 8 bits (ex: `01001000`).
3.  **Bits para Visual**: A sequência de bits é mapeada para caracteres. Por padrão, `1` se torna `█` e `0` se torna um espaço em branco.
4.  **Formatação**: O resultado é formatado com um `>` no início, um `.` no final e quebras de linha a cada 64 caracteres para facilitar a leitura.

### Processo de Decodificação e Reprodução

1.  **Extração**: O interpretador lê o arquivo `.txt` e extrai o conteúdo entre os marcadores `>` e `.`.
2.  **Visual para Bits**: Os caracteres visuais são convertidos de volta para uma string de '1's e '0's.
3.  **Bits para Texto**: A string de bits é agrupada em blocos de 8, convertida para bytes e, finalmente, decodificada de volta para o texto original em `UTF-8`.
4.  **Geração de Áudio**: Para a reprodução, um arquivo de áudio `.wav` é gerado dinamicamente:
    - Para cada bit `1`, uma onda quadrada com a frequência definida é gerada pela duração especificada.
    - Para cada bit `0`, um período de silêncio é gerado.
5.  **Reprodução e Sincronização**: O áudio é tocado usando bibliotecas nativas do sistema operacional, enquanto uma `thread` separada cuida de destacar o bit correspondente na interface gráfica em sincronia com o som.

## Tecnologias Utilizadas

- **Python 3**: Linguagem principal do projeto.
- **Tkinter**: Biblioteca padrão do Python para a criação das interfaces gráficas.
- **Pillow (PIL)**: Usada para manipular e exibir as imagens dos QR Codes.
- **qrcode**: Biblioteca para a geração dos QR Codes.

## Como Executar

### Pré-requisitos

- **Python 3**: https://www.python.org/downloads/
- **Bibliotecas Python**: `qrcode` e `Pillow`.
- **Player de Áudio (Linux/macOS)**: O interpretador tentará usar um dos seguintes comandos para tocar o áudio: `afplay` (macOS), `aplay` (Linux) ou `ffplay` (multiplataforma, parte do FFmpeg). Certifique-se de que um deles esteja instalado e acessível no seu sistema. No Windows, ele usa a biblioteca `winsound` que já vem com o Python.

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/John-BrenoF/codificador-bi.git
    cd codificador-bi
    ```

2.  Instale as dependências:
    ```bash
    pip install qrcode pillow
    ```

### Execução

Para rodar o **Codificador**:

```bash
python3 codificador.py
```

Para rodar o **Interpretador**:

```bash
python3 intrepletador.py
```
