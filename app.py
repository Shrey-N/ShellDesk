import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTreeView, QSplitter, QLabel, QStatusBar,
                             QPlainTextEdit, QToolBar, QPushButton, QTabWidget, QTabBar,
                             QFileIconProvider, QMenu, QFileDialog, QMessageBox)
from PyQt6.QtGui import QAction, QIcon, QFileSystemModel, QColor, QPixmap, QPainter
from PyQt6.QtCore import Qt, QDir, QSize, QPoint, QThread, pyqtSignal, QFileInfo
from editor.editor_widget import ShellLiteEditor
from editor.styles import COLORS, STYLESHEET

class EmojiFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.setIconProvider(QFileIconProvider())

class FileLoaderThread(QThread):
    loaded = pyqtSignal(str, str) 
    error = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.loaded.emit(content, self.path)
        except Exception as e:
            self.error.emit(str(e))

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(40) 
        self.setStyleSheet(f"background-color: {COLORS['bg_header']}; border-bottom: 1px solid {COLORS['border']};")
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)

        # File Menu
        self.btn_file = QPushButton("File")
        self.setup_menu_btn(self.btn_file)
        self.file_menu = QMenu(self)
        self.file_menu.setStyleSheet(f"background-color: {COLORS['bg_panel']}; color: {COLORS['text_main']}; border: 1px solid {COLORS['border']};")
        self.file_menu.addAction("New File", parent.new_file)
        self.file_menu.addAction("Open File...", parent.open_file)
        self.file_menu.addAction("Open Folder...", parent.open_folder)
        self.file_menu.addSeparator()
        self.file_menu.addAction("Save", parent.save_file)
        self.file_menu.addAction("Save As...", parent.save_as_file)
        self.file_menu.addSeparator()
        self.file_menu.addAction("Exit", parent.close)
        self.btn_file.setMenu(self.file_menu)
        self.layout.addWidget(self.btn_file)

        # Edit Menu
        self.btn_edit = QPushButton("Edit")
        self.setup_menu_btn(self.btn_edit)
        self.edit_menu = QMenu(self)
        self.edit_menu.setStyleSheet(f"background-color: {COLORS['bg_panel']}; color: {COLORS['text_main']}; border: 1px solid {COLORS['border']};")
        self.edit_menu.addAction("Undo", parent.undo)
        self.edit_menu.addAction("Redo", parent.redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction("Cut", parent.cut)
        self.edit_menu.addAction("Copy", parent.copy)
        self.edit_menu.addAction("Paste", parent.paste)
        self.btn_edit.setMenu(self.edit_menu)
        self.layout.addWidget(self.btn_edit)

        self.layout.addStretch()
        
        # Center Title
        self.center_title = QLabel("ShellDesk")
        self.center_title.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 13px; font-weight: 600;")
        self.layout.addWidget(self.center_title)
        
        self.layout.addStretch()

        # Run Button
        self.btn_run = QPushButton("▶ Run")
        self.btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_primary']}; 
                color: #1e1e1e; 
                border: none; 
                border-radius: 4px; 
                padding: 6px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #4cd6c0; }}
            QPushButton:pressed {{ background-color: #20b2aa; }}
        """)
        self.btn_run.clicked.connect(parent.run_script)
        self.layout.addWidget(self.btn_run)

    def setup_menu_btn(self, btn):
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {COLORS['text_dim']};
                background: transparent;
                border: none;
                font-size: 13px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{ color: {COLORS['text_main']}; background-color: #3f3f46; border-radius: 4px; }}
            QPushButton:menu-indicator {{ width: 0px; }}
        """)

class ShellDeskWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1100, 750)
        self.setWindowTitle("ShellDesk Editor")
        self.setWindowIcon(QIcon("editor/icon.png")) # Placeholder if exists
        
        # Setup Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Custom Title Bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        # 2. Main Content Splitter (Sidebar <-> Editor/Output)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Setup Sidebar
        self.setup_sidebar()
        self.splitter.addWidget(self.sidebar_container)

        # Setup Editor Area (Vertical Splitter: Tabs ^ Output v)
        self.editor_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed) # Hook into tab change
        # Tab Styling
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background: {COLORS['editor_bg']}; }}
            QTabBar::tab {{
                background: {COLORS['bg_panel']};
                color: {COLORS['text_dim']};
                padding: 8px 16px;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 2px solid {COLORS['border']}; 
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['editor_bg']};
                color: {COLORS['text_main']};
                border-bottom: 2px solid {COLORS['accent_primary']};
            }}
            QTabBar::close-button {{ subcontrol-position: right; margin-left: 5px; }}
            QTabBar::close-button:hover {{ background: #e81123; border-radius: 2px; }}
        """)
        self.editor_splitter.addWidget(self.tabs)

        # Output Console
        self.output_console = QPlainTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setPlaceholderText(">> Run output will appear here...")
        self.output_console.setStyleSheet(f"background-color: {COLORS['bg_dark']}; color: {COLORS['text_main']}; border-top: 1px solid {COLORS['border']}; font-family: 'Consolas', monospace; padding: 10px;")
        self.editor_splitter.addWidget(self.output_console)
        
        # Ratios
        self.editor_splitter.setStretchFactor(0, 3)
        self.editor_splitter.setStretchFactor(1, 1)

        self.splitter.addWidget(self.editor_splitter)
        
        self.splitter.setStretchFactor(0, 1) # Sidebar
        self.splitter.setStretchFactor(1, 5) # Editor
        
        self.main_layout.addWidget(self.splitter)

        # 3. Status Bar
        self.status_label = QLabel(" Ready " + u"\U0001F680") # Rocket
        self.status_label.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px; padding: 0 10px;")
        
        self.statusBar().addWidget(self.status_label)
        self.statusBar().setStyleSheet(f"background-color: {COLORS['status_bg_dark']}; border-top: 1px solid {COLORS['border']}; color: white;")
        
        self.open_files = {}

    def setup_sidebar(self):
        self.sidebar_container = QWidget()
        layout = QVBoxLayout(self.sidebar_container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_model = EmojiFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(os.getcwd()))
        
        # Styling
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        
        # Hide standard columns (Size, Type, Date) - keep Name
        for i in range(1, 4):
            self.tree_view.setColumnHidden(i, True)
            
        self.tree_view.clicked.connect(self.on_file_clicked)
        layout.addWidget(self.tree_view)

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        path_to_remove = None
        for path, w in self.open_files.items():
            if w == widget:
                path_to_remove = path
                break
        if path_to_remove:
            del self.open_files[path_to_remove]
        self.tabs.removeTab(index)

    def on_tab_changed(self, index):
        if index == -1:
            self.status_label.setText(" Ready ")
            return
        
        widget = self.tabs.widget(index)
        current_path = None
        for path, w in self.open_files.items():
            if w == widget:
                current_path = path
                break
        
        if current_path:
            self.status_label.setText(f" Editing: {os.path.basename(current_path)} ")
        else:
            self.status_label.setText(" Editing: Untitled ")

    def get_current_editor(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, ShellLiteEditor):
            return widget
        return None

    def undo(self):
        editor = self.get_current_editor()
        if editor: editor.undo()

    def redo(self):
        editor = self.get_current_editor()
        if editor: editor.redo()

    def cut(self):
        editor = self.get_current_editor()
        if editor: editor.cut()

    def copy(self):
        editor = self.get_current_editor()
        if editor: editor.copy()

    def paste(self):
        editor = self.get_current_editor()
        if editor: editor.paste()

    def run_script(self):
        current_editor = self.tabs.currentWidget()
        if not current_editor or not isinstance(current_editor, ShellLiteEditor):
            self.output_console.appendPlainText("Error: No active script to run.\n")
            return

        self.output_console.clear()
        self.output_console.appendPlainText(">> Executing script...\n")
        
        script_content = current_editor.text()
        temp_path = os.path.join(os.getcwd(), "temp_script.shl") 
        
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(script_content)
        except Exception as e:
            self.output_console.appendPlainText(f"Error saving temp file: {e}")
            return

        import subprocess
        env = os.environ.copy()
        
        # Fix PYTHONPATH to include the 'shell-lite' directory so 'shell_lite' module can be imported
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Append 'shell-lite' to PYTHONPATH
        shell_lite_path = os.path.join(project_root, "shell-lite")
        env["PYTHONPATH"] = shell_lite_path + os.pathsep + env.get("PYTHONPATH", "")
        
        # Using shell_lite.main instead of shell_lite.src.main
        cmd = [sys.executable, "-m", "shell_lite.main", temp_path]

        try:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                cwd=os.getcwd(),
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                self.output_console.appendPlainText(stdout)
            if stderr:
                self.output_console.appendPlainText("Errors:\n" + stderr)
                
            self.output_console.appendPlainText(f"\n[Exited with code {process.returncode}]")
            
        except Exception as e:
            self.output_console.appendPlainText(f"Execution failed: {e}")
            
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

    def on_file_clicked(self, index):
        if not index: 
             return
        path = self.file_model.filePath(index)
        
        if os.path.isdir(path):
            # If user clicked a folder, maybe expand/collapse (default behavior)
            # but we can't 'edit' it.
            return

        if os.path.isfile(path):
            if path in self.open_files:
                self.tabs.setCurrentWidget(self.open_files[path])
                self.status_label.setText(f" Switched to: {os.path.basename(path)} ")
                return
            
            self.status_label.setText(f" Loading: {os.path.basename(path)}... ")
            self.loader_thread = FileLoaderThread(path)
            self.loader_thread.loaded.connect(self.on_file_loaded)
            self.loader_thread.error.connect(self.on_file_error)
            self.loader_thread.start()

    def on_file_loaded(self, content, path):
        new_editor = ShellLiteEditor()
        new_editor.setText(content)
        filename = os.path.basename(path)
        index = self.tabs.addTab(new_editor, filename)
        self.tabs.setCurrentIndex(index)
        self.open_files[path] = new_editor
        self.status_label.setText(f" Editing: {filename} ")

    def on_file_error(self, err_msg):
        self.status_label.setText(f" Error: {err_msg} ")

    def new_file(self):
        new_editor = ShellLiteEditor()
        index = self.tabs.addTab(new_editor, "Untitled.shl") # Default extension hint
        self.tabs.setCurrentIndex(index)
        self.status_label.setText(" Created new file ")

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "ShellLite Files (*.sh *.shl *.oka);;All Files (*)")
        if path:
            self.on_file_clicked(self.file_model.index(path))

    def open_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Open Folder", os.getcwd())
        if dir_path:
            self.tree_view.setRootIndex(self.file_model.index(dir_path))
            self.status_label.setText(f" Workspace: {dir_path} ")

    def save_file(self):
        current_editor = self.tabs.currentWidget()
        if not current_editor or not isinstance(current_editor, ShellLiteEditor):
            return
            
        current_path = None
        for path, widget in self.open_files.items():
            if widget == current_editor:
                current_path = path
                break
                
        if current_path:
            try:
                with open(current_path, 'w', encoding='utf-8') as f:
                    f.write(current_editor.text())
                self.status_label.setText(f" Saved: {os.path.basename(current_path)} ")
            except Exception as e:
                self.status_label.setText(f" Error saving: {e} ")
        else:
            self.save_as_file()

    def save_as_file(self):
        current_editor = self.tabs.currentWidget()
        if not current_editor or not isinstance(current_editor, ShellLiteEditor):
            return
            
        # Get suggested filename from tab text
        index = self.tabs.indexOf(current_editor)
        suggested_name = self.tabs.tabText(index)
        if "*" in suggested_name: suggested_name = suggested_name.replace("*", "")
        
        path, _ = QFileDialog.getSaveFileName(self, "Save File As", suggested_name, "ShellLite Files (*.shl *.sh);;All Files (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(current_editor.text())
                    
                self.tabs.setTabText(index, os.path.basename(path))
                
                # Update map
                old_path = None
                for p, w in self.open_files.items():
                    if w == current_editor:
                        old_path = p
                        break
                if old_path:
                    del self.open_files[old_path]
                self.open_files[path] = current_editor
                
                self.status_label.setText(f" Saved as: {os.path.basename(path)} ")
            except Exception as e:
                self.status_label.setText(f" Error saving: {e} ")
