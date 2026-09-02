# Chronometer

**Versão:** 0.4.7

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

- **Presets de duração** — 1 a 5 minutos, depois 10, 15, 20, 25, 30, 45 e 60 minutos
- **Tempo manual** — campo editável com botões +/− (1 a 180 minutos)
- **Avisos visuais por cor** — branco (normal), laranja (< 1 min), vermelho (< 0 min)
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
- pytest (execução dos testes)
- pyinstaller ou nuitka (build de executáveis)

### Instalação
```bash
# Apenas para executar a aplicação
python3 -m pip install PyQt6

# Para desenvolvimento completo (incluindo traduções e build)
python3 -m pip install PyQt6 polib pyinstaller pytest
```

No Windows, pode utilizar `py -3 -m pip` em vez de `python3 -m pip`.

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

As instruções seguintes assumem que o código foi obtido para uma pasta que contém a pasta `chronometer/`.
É necessário ter Python 3.10 ou superior e PyQt6 instalados.

### Linux

```bash
cd /caminho/para/o/directorio-que-contem-chronometer
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install PyQt6
python3 -m chronometer
```

### Windows

```cmd
cd C:\caminho\para\o\directorio-que-contem-chronometer
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install PyQt6
py -3 -m chronometer
```

> **Nota:** `python3 -m chronometer` ou `py -3 -m chronometer` deve ser executado a partir do directório que **contém** a pasta `chronometer/`, não de dentro dela.

Para execução direta durante debug, dentro da pasta `chronometer/`, também pode executar:

```bash
python3 __main__.py
```

## Compilar para Executável

Para compilar a aplicação de forma correta, garantindo que todos os recursos (ícones, traduções e ficheiro desktop) sejam incluídos, utilize o script `build.py` fornecido.
O processo oficial não utiliza o ficheiro `Chronometer.spec`.

### Passo 1: Preparar o ambiente

**Importante:** Todos os comandos devem ser executados **dentro** da pasta `chronometer/`.

```bash
# Linux
cd /caminho/para/o/directorio-que-contem-chronometer/chronometer
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install PyQt6 polib pyinstaller

# Windows (CMD)
cd C:\caminho\para\o\directorio-que-contem-chronometer\chronometer
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install PyQt6 polib pyinstaller
```

### Passo 2: Compilar traduções

Este passo só é necessário quando os ficheiros `.po` forem alterados. Deve ser executado dentro da pasta `chronometer/`:

```bash
python3 i18n/compile.py
```

No Windows:

```cmd
py -3 i18n\compile.py
```

### Passo 3: Gerar o executável

Dentro da pasta `chronometer/`, execute:

```bash
python3 build.py
```

No Windows:

```cmd
py -3 build.py
```

O executável será criado na pasta `dist/`:

- Linux: `dist/Chronometer`
- Windows: `dist/Chronometer.exe`

O script inclui automaticamente os ficheiros `.mo`, os ícones e o ficheiro `chronometer.desktop` existentes no momento do build.

### Executar o executável

No Linux:

```bash
./dist/Chronometer
```

No Windows:

```cmd
dist\Chronometer.exe
```

O build deve ser executado no sistema operativo alvo. O ficheiro `Chronometer.spec` contém configuração gerada localmente e não é utilizado pelo processo oficial.

## Configuração

As preferências são guardadas em `~/.chronometer/config.json`:

| Chave | Valores | Predefinição |
|---|---|---|
| `last_monitor_index` | Índice inteiro do monitor | `1` |
| `language` | `pt_PT`, `en_US` ou `null` | `null` |
| `dark_mode` | `true` ou `false` | `false` |

O índice do monitor é validado no arranque e é usado um fallback quando o monitor guardado já não existe.

Os testes usam um diretório temporário e não devem alterar este ficheiro.

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

### Ficheiros Chave

- `chronometer/i18n/__init__.py` — `setup_i18n(lang)` configura gettext
- `chronometer/i18n/compile.py` — Compila `.po` → `.mo` usando polib
- `chronometer/i18n/test_i18n.py` — Testa se as traduções carregam corretamente

Mensagens com valores variáveis usam placeholders, por exemplo `{count}` e `{monitor_name}`. O template deve ser traduzido antes de aplicar `.format()`.

## Testes

Na raiz do projeto:

```bash
python test_config.py
PYTHONPATH=.. python i18n/test_i18n.py
```

Quando `pytest` estiver instalado, os testes podem ser descobertos a partir da raiz do pacote-pai:

```bash
PYTHONPATH=.. pytest -q
```

## Instalação através do ficheiro desktop (Linux)

O ficheiro `chronometer.desktop` assume que o executável `Chronometer` está disponível no `PATH`.

Para uma instalação apenas do utilizador:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps
cp dist/Chronometer ~/.local/bin/Chronometer
cp chronometer.desktop ~/.local/share/applications/
cp icon/chronometer-stopwatch-svgrepo-com.svg ~/.local/share/icons/hicolor/scalable/apps/
chmod +x ~/.local/bin/Chronometer
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

Se `~/.local/bin` não estiver no `PATH`, altere `Exec` no ficheiro desktop para o caminho absoluto do executável.

O ficheiro desktop e o ícone não são instalados automaticamente pelo build.

## Contribuição

1. Criar e ativar um ambiente virtual.
2. Instalar as dependências de runtime e desenvolvimento.
3. Executar os testes antes e depois das alterações.
4. Ao alterar textos traduzíveis, atualizar os ficheiros `.po` e recompilar os `.mo`.
5. Validar o build no sistema operativo alvo.
6. Manter alterações focadas e atualizar o README quando o comportamento mudar.

## Problemas conhecidos

- O countdown continua a mostrar tempo negativo depois de `00:00` até ser parado manualmente.
- O build PyInstaller deve ser executado no sistema operativo alvo.
- No Linux, o PyInstaller ignora o parâmetro `.ico` como ícone do executável; a integração visual depende do `.desktop` e da instalação do ícone.
- A janela de output requer uma sessão gráfica e o comportamento com múltiplos monitores depende do Qt, do compositor e da sessão X11/Wayland.
- O aviso de `libtiff.so.5` pode aparecer durante o build quando essa biblioteca não está instalada no sistema.

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
