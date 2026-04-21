# ---------------------------------------------------------------------------
# Todas as cores, tamanhos de fonte e valores visuais centralizados aqui.
# Para ajustar o visual da aplicação basta alterar este ficheiro.
# ---------------------------------------------------------------------------

# ---- Temas do painel de controlo (MainWindow) ----------------------------

LIGHT = {
    "bg":                "#f5f5f5",
    "text":              "#1a1a1a",
    "text_muted":        "#333",
    "timer_bg":          "#f9f5ee",
    "timer_text":        "#222",
    "presets_bg":        "#efe4cf",
    "presets_border":    "#d8ccb8",
    "preset_btn_bg":     "#fff7eb",
    "preset_btn_border": "#c8bca8",
    "btn_bg":            "#f4f4f4",
    "btn_border":        "#cfcfcf",
    "toggle_bg":         "#e8e8e8",
    "toggle_border":     "#cfcfcf",
    "status_text":       "#333",
    "footer_text":       "#333",
}

DARK = {
    "bg":                "#1e1e1e",
    "text":              "#ddd",
    "text_muted":        "#aaa",
    "timer_bg":          "#2d2d2d",
    "timer_text":        "#f0f0f0",
    "presets_bg":        "#2a2a2a",
    "presets_border":    "#444",
    "preset_btn_bg":     "#333",
    "preset_btn_border": "#555",
    "btn_bg":            "#333",
    "btn_border":        "#555",
    "toggle_bg":         "#444",
    "toggle_border":     "#666",
    "status_text":       "#aaa",
    "footer_text":       "#888",
}

# ---- Botão Call Attention (igual nos dois temas) -------------------------

ATTENTION = {
    "bg":     "#c62828",
    "border": "#8e0000",
    "text":   "white",
}

# ---- Janela de saída (TimerWindow — sempre fundo preto) ------------------

OUTPUT = {
    "bg":            "black",
    "time_normal":   "white",
    "time_warn":     "#ff9f0a",   # < 5 min
    "time_danger":   "#ff3b30",   # < 2 min
    "flash_red":     "#d50000",
    "flash_white":   "white",
    "flash_contrast":"white",     # cor do texto sobre fundo vermelho
    "flash_contrast_white":"black", # cor do texto sobre fundo branco
    "clock_text":    "#888888",
}

# ---- Limites de tempo (em segundos) para mudança de cor ------------------

TIME_WARN_SECS   = 300   # 5 minutos
TIME_DANGER_SECS = 120   # 2 minutos

# ---- Tamanhos de fonte ---------------------------------------------------

FONT = {
    "timer_output":  "220px",
    "timer_main":    "64px",
    "clock_output":  "52px",
    "btn_large":     "22px",
    "btn_attention": "20px",
    "btn_preset":    "16px",
    "btn_monitor":   "14px",
    "footer":        "14px",
    "status":        "13px",
    "toggle":        "12px",
}

# ---- Família de fonte principal ------------------------------------------

FONT_FAMILY = "Verdana"

# ---- Timings (ms) --------------------------------------------------------

FLASH_INTERVAL_MS   = 250
FLASH_MAX_TICKS     = 8      # 8 × 250 ms = 2 segundos
COUNTDOWN_INTERVAL  = 1000
CLOCK_INTERVAL      = 1000

# ---- Escala do texto na janela de output (segundo monitor) ----------------
# Proporção em relação ao tamanho da janela (0.0 – 1.0)

OUTPUT_TIMER_H_RATIO = 0.45   # % da altura da janela
OUTPUT_TIMER_W_RATIO = 0.22   # % da largura da janela  (usa-se o menor)
OUTPUT_CLOCK_RATIO   = 0.60   # % do tamanho do timer
OUTPUT_CLOCK_MIN_PX  = 30     # tamanho mínimo do relógio em px


# ---- Funções de construção de stylesheets --------------------------------

def build_control_styles(dark: bool) -> dict[str, str]:
    """Devolve um dicionário com as stylesheets para todos os widgets do
    painel de controlo (MainWindow)."""
    t = DARK if dark else LIGHT
    f = FONT
    a = ATTENTION
    return {
        "background": f"background-color: {t['bg']};",
        "status": f"font-size: {f['status']}; color: {t['status_text']};",
        "timer": (
            f"font-size: {f['timer_main']}; font-family: {FONT_FAMILY}; font-weight: 700;"
            f"color: {t['timer_text']}; background: {t['timer_bg']};"
            f"border-radius: 10px; padding: 12px;"
        ),
        "presets_box": (
            f"background-color: {t['presets_bg']};"
            f"border: 1px solid {t['presets_border']}; border-radius: 10px;"
        ),
        "preset_btn": (
            f"font-size: {f['btn_preset']}; font-weight: 600; color: {t['text']};"
            f"background-color: {t['preset_btn_bg']};"
            f"border: 1px solid {t['preset_btn_border']}; border-radius: 8px;"
        ),
        "control_btn": (
            f"font-size: {f['btn_large']}; font-weight: 700; color: {t['text']};"
            f"background-color: {t['btn_bg']};"
            f"border: 1px solid {t['btn_border']}; border-radius: 10px;"
        ),
        "monitor_btn": (
            f"font-size: {f['btn_monitor']}; color: {t['text']};"
            f"background-color: {t['btn_bg']};"
            f"border: 1px solid {t['btn_border']}; border-radius: 8px;"
        ),
        "attention_btn": (
            f"font-size: {f['btn_attention']}; font-weight: 700; color: {a['text']};"
            f"background-color: {a['bg']}; border-radius: 10px;"
            f"border: 1px solid {a['border']};"
        ),
        "toggle_btn": (
            f"font-size: {f['toggle']}; border-radius: 6px; padding: 2px 8px;"
            f"color: {t['text']}; background-color: {t['toggle_bg']};"
            f"border: 1px solid {t['toggle_border']};"
        ),
        "footer": f"font-size: {f['footer']}; color: {t['footer_text']};",
        "spinbox": (
            f"font-size: {f['btn_preset']}; font-weight: 600; color: {t['text']};"
            f"background-color: {t['preset_btn_bg']};"
            f"border: 1px solid {t['preset_btn_border']}; border-radius: 8px;"
            f"padding: 4px 8px;"
        ),
    }


def output_bg_style() -> str:
    """Stylesheet de fundo da janela de output."""
    return f"background-color: {OUTPUT['bg']};"


def output_time_style(color: str, size_px: int = 220) -> str:
    """Stylesheet do label de tempo na janela de output."""
    return (
        f"color: {color}; font-size: {size_px}px;"
        f" font-family: {FONT_FAMILY}; font-weight: 700;"
    )


def output_clock_style(size_px: int = 52) -> str:
    """Stylesheet do relógio na janela de output."""
    return (
        f"color: {OUTPUT['clock_text']}; font-size: {size_px}px;"
        f" font-family: {FONT_FAMILY}; font-weight: 400;"
    )


def output_flash_bg(red: bool) -> str:
    """Stylesheet de fundo durante o flash de atenção."""
    if red:
        return f"background-color: {OUTPUT['flash_red']};"
    return f"background-color: {OUTPUT['flash_white']};"
