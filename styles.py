COLORS = {
    "bg_dark": "#18181b",      
    "bg_panel": "#202023",     
    "bg_header": "#27272a",    
    "accent_primary": "#20b2aa", 
    "accent_secondary": "#c678dd", 
    "text_main": "#e0e0e0",
    "text_dim": "#757575",
    "border": "#333333",
    "selection": "#3e4451",
    "editor_bg": "#1e1e1e",
    "status_bg": "#007acc",     
    "status_bg_dark": "#2d2d2d"
}
STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS["bg_dark"]};
    border: 1px solid {COLORS["border"]};
}}
QWidget {{
    background-color: {COLORS["bg_dark"]};
    color: {COLORS["text_main"]};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}}
/* === Sidebar (File Explorer) === */
QTreeView {{
    background-color: {COLORS["bg_panel"]};
    border-right: 1px solid {COLORS["border"]};
    padding: 5px;
    outline: none;
}}
QTreeView::item {{
    padding: 4px;
    border-radius: 4px;
}}
QTreeView::item:hover {{
    background-color: #2c2c30;
}}
QTreeView::item:selected {{
    background-color: #3e3e42;
    color: white;
}}
/* === Splitter === */
QSplitter::handle {{
    background-color: {COLORS["border"]};
    width: 1px;
}}
/* === Editor & Output === */
QsciScintilla {{
    border: none;
    background-color: {COLORS["editor_bg"]};
    font-family: 'Consolas', monospace;
}}
QPlainTextEdit {{
    background-color: {COLORS["bg_dark"]};
    border-top: 1px solid {COLORS["border"]};
    color: {COLORS["text_main"]};
    padding: 8px;
    font-family: 'Consolas', monospace;
}}
/* === Toolbar / Actions === */
QToolBar {{
    background-color: {COLORS["bg_panel"]};
    border-bottom: 1px solid {COLORS["border"]};
    padding: 2px;
    spacing: 10px;
}}
QToolButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 4px 10px;
    color: {COLORS["text_main"]};
    font-weight: 600;
}}
QToolButton:hover {{
    background-color: #333333;
    color: {COLORS["accent_primary"]};
}}
QToolButton:pressed {{
    background-color: #252526;
}}
/* === Status Bar === */
QStatusBar {{
    background-color: {COLORS["status_bg_dark"]}; /* Subtle dark grey */
    color: white;
    font-weight: normal;
    border-top: 1px solid {COLORS["border"]};
}}
/* === Scrollbars === */
QScrollBar:vertical {{
    background: {COLORS["bg_dark"]};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: #424242;
    border-radius: 5px;
    min-height: 20px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0px; }}
"""
