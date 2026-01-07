from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QFont, QFontMetrics
from PyQt6.Qsci import QsciScintilla, QsciLexerCustom
from editor.styles import COLORS
class ShellLiteEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUtf8(True)
        self.setEolMode(QsciScintilla.EolMode.EolWindows)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        font = QFont("Fira Code", 11)
        if not font.exactMatch():
            font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setColor(QColor(COLORS["text_main"]))
        self.setPaper(QColor(COLORS["editor_bg"]))
        font_metrics = QFontMetrics(font)
        self.setMarginWidth(0, font_metrics.horizontalAdvance("00000") + 10)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor(COLORS["bg_panel"]))
        self.setMarginsForegroundColor(QColor(COLORS["text_dim"]))
        self.setCaretForegroundColor(QColor(COLORS["accent_primary"]))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#1a1a1d"))
        self.setSelectionBackgroundColor(QColor(COLORS["selection"]))
        self.setSelectionForegroundColor(QColor(COLORS["text_main"]))
        from editor.lexer import ShellLiteLexer
        self.lexer = ShellLiteLexer(self)
        self.setLexer(self.lexer)
        from PyQt6.Qsci import QsciAPIs
        self.api = QsciAPIs(self.lexer)
        keywords = [
            "say", "print", "show", "ask", "if", "else", "elif", "unless",
            "while", "until", "for", "forever", "repeat", "times", "stop", "skip",
            "return", "give", "fn", "is", "break", "continue", "in", "make", "new",
            "thing", "extends", "has", "can", "to", "try", "catch", "always",
            "throw", "error", "import", "use", "as", "share", "exit", "const",
            "true", "false", "yes", "no"
        ]
        for k in keywords:
            self.api.add(k)
        stdlib = [
            "math.pi", "math.e", "math.sqrt", "math.sin", "math.cos", "math.floor", "math.ceil", "math.random",
            "time.date", "time.year", "time.month", "time.day", "time.sleep",
            "color.red", "color.green", "color.blue", "color.yellow", "color.bold",
            "path.basename", "path.dirname", "path.ext", "path.exists", "path.join",
            "env.get", "env.has", "env.set",
            "re.match", "re.findall", "re.replace", "re.split",
            "json_stringify", "json_parse"
        ]
        for s in stdlib:
            self.api.add(s)
        self.api.prepare()
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)
        self.textChanged.connect(self.on_text_changed)
        from PyQt6.QtCore import QTimer
        self.scan_timer = QTimer()
        self.scan_timer.setSingleShot(True)
        self.scan_timer.setInterval(2000)
        self.scan_timer.timeout.connect(self.scan_document)
        self.scan_document()
    def on_text_changed(self):
        self.scan_timer.start()
    def scan_document(self):
        import re
        code = self.text()
        funcs = re.findall(r'(?:to|fn)\s+([a-zA-Z_]\w*)', code)
        vars_ = re.findall(r'([a-zA-Z_]\w*)\s*=', code)
        if not hasattr(self, 'added_tokens'):
            self.added_tokens = set()
        new_tokens = set(funcs + vars_)
        for token in new_tokens:
            if token not in self.added_tokens:
                self.api.add(token)
                self.added_tokens.add(token)
        self.api.prepare()
