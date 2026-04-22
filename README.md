# Chronometer

Cronómetro para apresentações e talks, com painel de controlo e janela de output para segundo monitor.

## Funcionalidades

- **Presets de duração** — 10, 15, 20, 25, 30, 35, 45 e 60 minutos
- **Tempo manual** — campo editável com botões +/− (1 a 180 minutos)
- **Avisos visuais por cor** — branco (normal), laranja (< 5 min), vermelho (< 2 min)
- **Call Attention** — efeito flash vermelho/branco no segundo monitor
- **Seleção de monitor** — lista todos os monitores ligados, escolhe onde mostrar o output
- **Dark / Light mode** — alternância com um clique
- **Texto responsivo** — o timer e relógio ajustam-se à resolução do monitor
- **Fechar output clicando na hora** — esconde a janela sem fechar a aplicação

## Requisitos

- Python 3.10+
- PyQt6

```bash
pip install PyQt6
```

## Estrutura do Projeto

```
chronometer/
├── __init__.py          # Package marker
├── __main__.py          # Entry point (python -m chronometer)
├── app.py               # Cria QApplication e MainWindow
├── main_window.py       # Painel de controlo
├── timer_window.py      # Janela de output (segundo monitor)
├── icon/
│   ├── chronometer-stopwatch-svgrepo-com.svg  # Asset original
│   └── chronometer-stopwatch-svgrepo-com.ico  # Ícone para Windows/PyInstaller
└── theme.py             # Cores, fontes, tamanhos e stylesheets
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
python -m chronometer
```

> **Nota:** o comando deve ser executado a partir do directório que **contém** a pasta `chronometer/`, não de dentro dela. O `__main__.py` também suporta execução direta no caso de empacotamento ou debug local.

## Compilar para Executável

### Linux (PyInstaller)

```bash
cd /caminho/para/o/directorio_que_contem_chronometer
python3 -m venv .venv
source .venv/bin/activate
pip install PyQt6 pyinstaller
pyinstaller --onefile --windowed --name TalkChronometer chronometer/__main__.py
```

O executável fica em `dist/TalkChronometer`.

```bash
./dist/TalkChronometer
```

### Windows (PyInstaller)

```cmd
cd C:\caminho\para\o\directorio_que_contem_chronometer
python -m venv .venv
.venv\Scripts\activate
pip install PyQt6 pyinstaller
pyinstaller --onefile --windowed --icon chronometer\icon\chronometer-stopwatch-svgrepo-com.ico --name TalkChronometer chronometer\__main__.py
```

O executável fica em `dist\TalkChronometer.exe`.

### Comando rapido no Windows

Se ja tiveres o ambiente preparado, o comando principal para gerar o executavel e:

```cmd
pyinstaller --onefile --windowed --icon chronometer\icon\chronometer-stopwatch-svgrepo-com.ico --name TalkChronometer chronometer\__main__.py
```

O ícone da aplicação é o stopwatch SVG convertido para `.ico` e usado também na janela principal.

### Alternativa: Nuitka

```bash
cd /caminho/para/o/directorio_que_contem_chronometer
python3 -m venv .venv
source .venv/bin/activate
pip install PyQt6 nuitka
nuitka --standalone --onefile --enable-plugin=pyqt6 --disable-console chronometer/__main__.py -o TalkChronometer
```

> **Importante:** o executável gerado é específico do sistema operativo onde é compilado. Para gerar um `.exe` para Windows, é necessário compilar no Windows.

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
