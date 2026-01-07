from PyQt6.Qsci import QsciLexerCustom
from PyQt6.QtGui import QColor, QFont
class ShellLiteLexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.DEFAULT = 0
        self.KEYWORD = 1
        self.STRING = 2
        self.COMMENT = 3
        self.NUMBER = 4
        self.FUNCTION = 5
        self.OPERATOR = 6
        from editor.styles import COLORS
        self.colors = {
            self.DEFAULT: COLORS["text_main"],
            self.KEYWORD: "#ff79c6",
            self.STRING: "#f1fa8c",
            self.COMMENT: "#6272a4",
            self.NUMBER: "#bd93f9",
            self.FUNCTION: "#8be9fd",
            self.OPERATOR: "#ffb86c"
        }
        self.keywords = {
            "say", "print", "show", "ask", "if", "else", "elif", "unless",
            "while", "until", "for", "forever", "repeat", "times", "stop", "skip",
            "return", "give", "fn", "is", "break", "continue", "in", "make", "new",
            "thing", "extends", "has", "can", "to", "try", "catch", "always",
            "throw", "error", "import", "use", "as", "share", "exit", "const",
            "when"
        }
        import re
        token_spec = [
            ('COMMENT', r'#.*'),
            ('STRING',  r'"[^"]*"|\'[^\']*\''),
            ('NUMBER',  r'\d+(\.\d*)?'),
            ('KEYWORD', r'\b(' + '|'.join(self.keywords) + r')\b'),
            ('OPERATOR', r'[+\-*/%=<>!&|^~]+'),
            ('SKIP',    r'[ \t\n]+'),
            ('MISC',    r'.'),
        ]
        self.tok_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in token_spec))
    def language(self):
        return "ShellLite"
    def description(self, style):
        if style == self.KEYWORD: return "Keyword"
        if style == self.STRING: return "String"
        if style == self.COMMENT: return "Comment"
        return "Default"
    def styleText(self, start, end):
        self.startStyling(start)
        full_text = self.parent().text()
        text_slice = full_text[start:end]
        for mo in self.tok_regex.finditer(text_slice):
            kind = mo.lastgroup
            value = mo.group()
            length = len(value.encode('utf-8')) 
            if kind == 'KEYWORD':
                self.setStyling(length, self.KEYWORD)
            elif kind == 'STRING':
                self.setStyling(length, self.STRING)
            elif kind == 'COMMENT':
                self.setStyling(length, self.COMMENT)
            elif kind == 'NUMBER':
                self.setStyling(length, self.NUMBER)
            elif kind == 'SKIP':
                self.setStyling(length, self.DEFAULT)
            else:
                self.setStyling(length, self.DEFAULT)
    def defaultColor(self, style):
        return QColor(self.colors.get(style, "#d4d4d4"))
    def defaultPaper(self, style):
        return QColor("#1e1e1e")
    def defaultFont(self, style):
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        if style == self.KEYWORD:
            font.setBold(True)
        return font
