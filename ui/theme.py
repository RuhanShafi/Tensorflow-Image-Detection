# Catppuccin Mocha palette
MOCHA = {
    "base":     "#1e1e2e",
    "mantle":   "#181825",
    "crust":    "#11111b",
    "text":     "#cdd6f4",
    "subtext1": "#bac2de",
    "subtext0": "#a6adc8",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
    "overlay0": "#6c7086",
    "blue":     "#89b4fa",
    "lavender": "#b4befe",
    "sapphire": "#74c7ec",
    "green":    "#a6e3a1",
    "yellow":   "#f9e2af",
    "peach":    "#fab387",
    "red":      "#f38ba8",
    "mauve":    "#cba6f7",
    "pink":     "#f5c2e7",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {MOCHA["base"]};
    color: {MOCHA["text"]};
    font-family: "JetBrainsMono Nerd Font", "JetBrains Mono", sans-serif;
    font-size: 13px;
}}

QToolBar {{
    background-color: {MOCHA["mantle"]};
    border: none;
    padding: 4px;
    spacing: 6px;
}}

QToolBar QToolButton {{
    background-color: transparent;
    color: {MOCHA["text"]};
    padding: 6px 10px;
    border-radius: 6px;
}}

QToolBar QToolButton:hover {{
    background-color: {MOCHA["surface0"]};
    color: {MOCHA["lavender"]};
}}

QTabWidget::pane {{
    border: 1px solid {MOCHA["surface0"]};
    border-radius: 8px;
    background-color: {MOCHA["mantle"]};
}}

QTabBar::tab {{
    background-color: {MOCHA["surface0"]};
    color: {MOCHA["subtext0"]};
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background-color: {MOCHA["mantle"]};
    color: {MOCHA["mauve"]};
    font-weight: bold;
}}

QPushButton {{
    background-color: {MOCHA["surface1"]};
    color: {MOCHA["text"]};
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
}}

QPushButton:hover {{
    background-color: {MOCHA["surface2"]};
}}

QPushButton:pressed {{
    background-color: {MOCHA["overlay0"]};
}}

QComboBox {{
    background-color: {MOCHA["surface0"]};
    color: {MOCHA["text"]};
    border: 1px solid {MOCHA["surface2"]};
    border-radius: 6px;
    padding: 4px 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {MOCHA["surface0"]};
    color: {MOCHA["text"]};
    selection-background-color: {MOCHA["surface2"]};
    selection-color: {MOCHA["lavender"]};
}}

QLabel {{
    color: {MOCHA["text"]};
}}

QLabel#resultLabel {{
    color: {MOCHA["green"]};
    font-size: 18px;
    font-weight: bold;
}}

QLabel#confidenceLabel {{
    color: {MOCHA["subtext0"]};
    font-size: 12px;
}}

QScrollBar:vertical {{
    background: {MOCHA["mantle"]};
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: {MOCHA["surface2"]};
    border-radius: 5px;
}}
"""