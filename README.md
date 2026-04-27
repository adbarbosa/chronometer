# Chronometer

**Versão:** 0.4.3

Cronómetro para apresentações e talks, com painel de controlo e janela de output para segundo monitor. Suporta múltiplos idiomas (pt-PT, en-US).

## Índice
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Executar](#executar)
- [Compilar para Executável](#compilar-para-executável)
- [Internacionalização (i18n)](#internacionalização-i18n)
- [Personalização](#personalização)
- [Licença](#licença)

## Funcionalidades

- **Presets de duração** — 10, 15, 20, 25, 30, 35, 45 e 60 minutos
- **Tempo manual** — campo editável com botões +/− (1 a 180 minutos)
- **Avisos visuais por cor** — branco (normal), laranja (< 5 min), vermelho (< 2 min)
- **Call Attention** — efeito flash vermelho/branco no segundo monitor
- **Seleção de monitor** — lista todos os monitores ligados, escolhe onde mostrar o output
- **Dark / Light mode** — alternância com um clique
- **Texto responsivo** — o timer e relógio ajustam-se à resolução do monitor
- **Fechar output clicando na hora** — esconde a janela sem fechar a aplicação
- **Internacionalização** — Suporte para português (Portugal) e inglês (EUA)
- **Menu Ajuda** — Acesso a informação do projeto e link para GitHub

## Requisitos

### Runtime
- Python 3.10+
- PyQt6

### Desenvolvimento (Traduções e Build)
- polib (compilação de traduções)
- pyinstaller ou nuitka (build de executáveis)

### Instalação
```bash
# Apenas para executar a aplicação
pip install PyQt6

# Para desenvolvimento completo (incluindo traduções e build)
pip install PyQt6 polib pyinstaller
```

## Estrutura do Projeto

```
chronometer/
├── __init__.py              # Package marker (v0.4.2)
├── __main__.py              # Entry point (python -m chronometer)
├── app.py                   # Cria QApplication, setup i18n
├── main_window.py           # Painel de controlo + menu Ajuda
├── about_dialog.py          # Diálogo Sobre Chronometer (v0.4.2)
├── timer_window.py          # Janela de output (segundo monitor)
├── theme.py                 # Cores, fontes, tamanhos, stylesheets
├── i18n/                    # Internacionalização
│   ├── __init__.py          # setup_i18n() - configuração de gettext
│   ├── compile.py           # Compilador .po → .mo (usa polib)
│   ├── chronometer.pot      # Template de traduções
│   ├── pt_PT.po             # Português (Portugal)
│   ├── en_US.po             # Inglês (EUA)
│   ├── test_i18n.py         # Testes de i18n
│   └── locales/             # Compilados (gerados)
│       ├── pt_PT/LC_MESSAGES/chronometer.mo
│       └── en_US/LC_MESSAGES/chronometer.mo
├── icon/
│   ├── chronometer-stopwatch-svgrepo-com.svg  # Asset original
│   └── chronometer-stopwatch-svgrepo-com.ico  # Ícone para Windows/PyInstaller
└── ...
```

## Executar

### Linux

```bash
cd /caminho/para/o/directorio_que_contem_chronometer
python3 -m chronometer
```

### Windows

```cmd
cd C:\caminho\para\o\directorio_que_contem_chronometer
python3 -m chronometer
```

> **Nota:** o comando deve ser executado a partir do directório que **contém** a pasta `chronometer/`, não de dentro dela. O `__main__.py` também suporta execução direta no caso de empacotamento ou debug local.

## Compilar para Executável

Para compilar a aplicação de forma correta, garantindo que todos os recursos (ícones e traduções) sejam incluídos, utilize o script de build fornecido.

### Passo 1: Preparar o ambiente

**Importante:** Todos os comandos devem ser executados **dentro** da pasta `chronometer/`.

```bash
# Linux
cd chronometer
python3 -m venv .venv
source .venv/bin/activate
pip install PyQt6 pyinstaller

# Windows (CMD)
cd chronometer
python3 -m venv .venv
.venv\Scripts\activate
pip install PyQt6 pyinstaller

# Windows (Git Bash / MINGW64)
cd chronometer
python3 -m venv .venv
source .venv/Scripts/activate
pip install PyQt6 pyinstaller
```

### Passo 2: Executar o Build

Execute o script `build.py` dentro da pasta do projeto:

```bash
python3 build.py
```

O executável final será gerado na pasta `dist/`.

### Passo 2.5: Compilar Traduções (Opcional)

Se alterou traduções, certifique-se de que estão compiladas antes de gerar o executável:

```bash
# Dentro da pasta chronometer/
python3 i18n/compile.py
```

O script `build.py` incluirá automaticamente os ficheiros `.mo` gerados no executável.

### Alternativa: Nuitka

```bash
cd /caminho/para/o/directorio_que_contem_chronometer
python3 -m venv .venv
source .venv/bin/activate
pip install nuitka
python3 -m nuitka --onefile --noconsole app.py
```

## Internacionalização (i18n)

Como as Traduções Funcionam

- **Detecção automática:** A aplicação detecta o idioma do sistema via `locale.getdefaultlocale()`
- **Fallback:** Se o idioma não for suportado, volta para pt_PT
- **Inicialização:** Em `app.py`, `setup_i18n()` é chamado antes de criar a UI

### Idiomas Suportados

- **pt_PT** — Português (Portugal) [padrão]
- **en_US** — Inglês (EUA)

### Adicionar Novo Idioma

1. **Criar novo ficheiro PO:**
   ```bash
   cp chronometer/i18n/chronometer.pot chronometer/i18n/xx_YY.po
   ```
   Substituir `xx_YY` pelo código do idioma (ex: `pt_BR`, `es_ES`, `fr_FR`)

2. **Traduzir strings no ficheiro .po:**
   - Abrir com Poedit, Lokalize, ou editor de texto
   - Preencher `msgstr` com a tradução para cada `msgid`
   - Exemplo:
     ```po
     msgid "Abrir"
     msgstr "Open"
     ```

3. **Compilar traduções:**
   ```bash
   cd chronometer
   python3 i18n/compile.py
   ```
   Isto gera ficheiros `.mo` em `i18n/locales/{xx_YY}/LC_MESSAGES/chronometer.mo`

4. **Testar:**
      ```bash
   LANG=xx_YY.UTF-8 python3 -m chronometer
   ```

### Como as Traduções Funcionam

- **Detecção automática:** A aplicação detecta o idioma do sistema via `locale.getdefaultlocale()`
- **Fallback:** Se o idioma não for suportado, volta para pt_PT
- **Inicialização:** Em `app.py`, `setup_i18n()` é chamado antes de criar a UI

### Ficheiros Chave

- `chronometer/i18n/__init__.py` — `setup_i18n(lang)` configura gettext
- `chronometer/i18n/compile.py` — Compila `.po` → `.mo` usando polib
- `chronometer/i18n/test_i18n.py` — Testa se as traduções carregam corretamente

## Personalização

Todas as cores, fontes, tamanhos e timings podem ser ajustados em `chronometer/theme.py`:

| Variável | Descrição |
|---|---|
| `LIGHT` / `DARK` | Paletas de cores dos temas |
| `OUTPUT` | Cores da janela de output |
| `FONT` | Tamanhos de fonte |
| `OUTPUT_TIMER_H_RATIO` | Escala do timer no output (% da altura) |
| `OUTPUT_TIMER_W_RATIO` | Escala do timer no output (% da largura) |
| `OUTPUT_CLOCK_RATIO` | Escala do relógio (% do timer) |
| `TIME_WARN_SECS` | Limite para aviso laranja (default: 300s) |
| `TIME_DANGER_SECS` | Limite para aviso vermelho (default: 120s) |

## Licença

Este projeto é de uso livre.
