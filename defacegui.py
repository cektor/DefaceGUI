#!/usr/bin/env python3
import sys
import os
import subprocess
import threading
import json
import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Qt platform plugin sorununu çözmek için ortam değişkenlerini ayarla
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
os.environ['QT_PLUGIN_PATH'] = ''

def check_deface_installed():
    """Deface paketinin kurulu olup olmadığını kontrol eder"""
    try:
        # Önce Python modülü olarak kontrol et
        subprocess.run(["python3", "-c", "import deface"], capture_output=True, check=True)
        # Sonra komut satırı aracı olarak kontrol et
        subprocess.run(["deface", "--help"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Eğer komut satırı aracı bulunamazsa PATH'i güncelle
        try:
            # Kullanıcı dizinindeki bin klasörünü PATH'e ekle
            user_bin = os.path.expanduser("~/.local/bin")
            if user_bin not in os.environ.get("PATH", ""):
                os.environ["PATH"] = user_bin + ":" + os.environ.get("PATH", "")
            # Tekrar dene
            subprocess.run(["deface", "--help"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

def install_dependencies():
    """Gerekli bağımlılıkları kurar"""
    try:
        # 1. pip kurulumu kontrolü ve kurulumu
        try:
            subprocess.run(["python3", "-m", "pip", "--version"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            # pip kurulu değil, kur
            subprocess.run(["pkexec", "apt", "update"], check=True)
            subprocess.run(["pkexec", "apt", "install", "-y", "python3-pip"], check=True)
        
        # 2. EXTERNALLY-MANAGED dosyasını kaldır
        subprocess.run(["pkexec", "rm", "-rf", "/usr/lib/python3.11/EXTERNALLY-MANAGED"], 
                     capture_output=True, check=False)
        
        # 3. deface kurulumu - birkaç yöntem dene
        install_success = False
        
        # Yöntem 1: Normal pip
        try:
            subprocess.run(["python3", "-m", "pip", "install", "deface"], check=True)
            install_success = True
        except subprocess.CalledProcessError:
            pass
        
        # Yöntem 2: --user ile
        if not install_success:
            try:
                subprocess.run(["python3", "-m", "pip", "install", "--user", "deface"], check=True)
                install_success = True
            except subprocess.CalledProcessError:
                pass
        
        # Yöntem 3: sudo ile
        if not install_success:
            try:
                subprocess.run(["pkexec", "python3", "-m", "pip", "install", "deface"], check=True)
                install_success = True
            except subprocess.CalledProcessError:
                pass
        
        # Yöntem 4: --break-system-packages ile
        if not install_success:
            try:
                subprocess.run(["python3", "-m", "pip", "install", "--break-system-packages", "deface"], check=True)
                install_success = True
            except subprocess.CalledProcessError:
                pass
        
        return install_success
    except Exception:
        return False

class DefaceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        


             
        
        self.setWindowTitle(self.tr("window_title"))
        self.setGeometry(100, 100, 950, 750)
        self.setMinimumSize(750, 550)
        self.setAcceptDrops(True)
        
        # Program ikonu ayarla
        icon_path = "/usr/share/pixmaps/defaceguilo.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Ayarlar dosyası
        self.settings_file = os.path.expanduser("~/.deface_gui_settings.json")
        self.load_settings()
        
        # Deface kurulum kontrolü
        self.check_deface_installation()
        
        self.init_ui()
    
    def check_deface_installation(self):
        """Deface kurulumunu kontrol eder ve gerekirse run.sh çalıştırır"""
        if not check_deface_installed():
            # Deface kurulu değil, kurulum script'ini çalıştır
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle(self.tr("deface_install_required"))
            msg.setText(self.tr("deface_install_question"))
            msg.setInformativeText(self.tr("deface_install_info"))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            
            if msg.exec_() == QMessageBox.Yes:
                # Kurulum progress dialogı göster
                progress = QProgressDialog(self.tr("installing_deface"), None, 0, 0, self)
                progress.setWindowModality(Qt.WindowModal)
                progress.show()
                QApplication.processEvents()
                
                # Bağımlılıkları kur
                if install_dependencies():
                    progress.close()
                    # Kurulum sonrası tekrar kontrol et
                    if check_deface_installed():
                        QMessageBox.information(self, self.tr("success"), self.tr("deface_installed_success"))
                    else:
                        # PATH'i yenile ve tekrar dene
                        user_bin = os.path.expanduser("~/.local/bin")
                        if user_bin not in os.environ.get("PATH", ""):
                            os.environ["PATH"] = user_bin + ":" + os.environ.get("PATH", "")
                        
                        if check_deface_installed():
                            QMessageBox.information(self, self.tr("success"), self.tr("deface_installed_success"))
                        else:
                            QMessageBox.information(self, self.tr("success"), self.tr("deface_install_success_restart"))
                else:
                    progress.close()
                    QMessageBox.critical(self, self.tr("error"), self.tr("deface_install_failed"))
            else:
                QMessageBox.warning(self, self.tr("warning"), self.tr("deface_required_warning"))
        
    def tr(self, key):
        return self.translations[self.current_language].get(key, key)
    
    def init_ui(self):
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Sol panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        left_panel.setContentsMargins(20, 20, 10, 20)
        
     
        left_panel.addLayout(header_layout)
        
        # Dosya seçimi grubu
        self.file_group = QGroupBox(self.tr("file_selection"))
        file_layout = QVBoxLayout(self.file_group)
        
        # Drag & Drop alanı
        self.drop_area = QLabel(self.tr("drag_drop"))
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setMinimumHeight(80)
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 8px;
                background-color: #3c3c3c;
                color: #aaaaaa;
                font-size: 14px;
            }
        """)
        file_layout.addWidget(self.drop_area)
        
        # Giriş dosyası
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText(self.tr("input_placeholder"))
        self.input_browse = QPushButton(self.tr("browse"))
        self.input_browse.clicked.connect(self.browse_input)
        self.input_label = QLabel(self.tr("input"))
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.input_browse)
        file_layout.addLayout(input_layout)
        
        # Çıkış dosyası
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText(self.tr("output_placeholder"))
        self.output_browse = QPushButton(self.tr("browse_output"))
        self.output_browse.clicked.connect(self.browse_output)
        self.output_label = QLabel(self.tr("output"))
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.output_browse)
        file_layout.addLayout(output_layout)
        
        left_panel.addWidget(self.file_group)
        
        # Seçenekler grubu
        self.options_group = QGroupBox(self.tr("anonymization_options"))
        options_layout = QVBoxLayout(self.options_group)
        
        # Anonimleştirme yöntemi
        method_layout = QHBoxLayout()
        self.method_label = QLabel(self.tr("method"))
        method_layout.addWidget(self.method_label)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["blur", "mosaic", "solid"])
        self.method_combo.setItemData(0, self.tr("tooltip_blur"), Qt.ToolTipRole)
        self.method_combo.setItemData(1, self.tr("tooltip_mosaic"), Qt.ToolTipRole)
        self.method_combo.setItemData(2, self.tr("tooltip_solid"), Qt.ToolTipRole)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        options_layout.addLayout(method_layout)
        
        # Ses koruma
        self.keep_audio = QCheckBox(self.tr("keep_audio"))
        self.keep_audio.setChecked(True)
        options_layout.addWidget(self.keep_audio)
        
        # Önizleme seçeneği
        self.preview_mode = QCheckBox(self.tr("preview_mode"))
        options_layout.addWidget(self.preview_mode)
        
        left_panel.addWidget(self.options_group)
        
        # Gelişmiş ayarlar
        self.advanced_group = QGroupBox(self.tr("advanced_settings"))
        advanced_layout = QVBoxLayout(self.advanced_group)
        
        # Threshold ayarı
        thresh_layout = QHBoxLayout()
        self.threshold_label = QLabel(self.tr("detection_threshold"))
        thresh_layout.addWidget(self.threshold_label)
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.1, 1.0)
        self.threshold_spin.setSingleStep(0.1)
        self.threshold_spin.setValue(0.2)
        self.threshold_spin.setToolTip(self.tr("tooltip_threshold"))
        thresh_layout.addWidget(self.threshold_spin)
        thresh_layout.addStretch()
        advanced_layout.addLayout(thresh_layout)
        
        # Mozaik boyutu
        mosaic_layout = QHBoxLayout()
        self.mosaic_label = QLabel(self.tr("mosaic_size"))
        mosaic_layout.addWidget(self.mosaic_label)
        self.mosaic_size = QSpinBox()
        self.mosaic_size.setRange(5, 50)
        self.mosaic_size.setValue(20)
        self.mosaic_size.setToolTip(self.tr("tooltip_mosaic_size"))
        mosaic_layout.addWidget(self.mosaic_size)
        mosaic_layout.addStretch()
        advanced_layout.addLayout(mosaic_layout)
        
        left_panel.addWidget(self.advanced_group)
        
        # İşlem butonu
        self.process_btn = QPushButton(self.tr("start_process"))
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setMinimumHeight(50)
        left_panel.addWidget(self.process_btn)
        
        # İlerleme çubuğu
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        left_panel.addWidget(self.progress)
        
        left_panel.addStretch()
        
        # Sağ panel
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(10, 20, 20, 20)
        
        # Log alanı
        self.log_group = QGroupBox(self.tr("process_log"))
        log_layout = QVBoxLayout(self.log_group)
        
        # Log kontrolleri
        log_controls = QHBoxLayout()
        self.clear_log_btn = QPushButton(self.tr("clear"))
        self.clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        self.save_log_btn = QPushButton(self.tr("save"))
        self.save_log_btn.clicked.connect(self.save_log)
        log_controls.addWidget(self.clear_log_btn)
        log_controls.addWidget(self.save_log_btn)
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        right_panel.addWidget(self.log_group)
        
        # İşlem geçmişi
        self.history_group = QGroupBox(self.tr("process_history"))
        history_layout = QVBoxLayout(self.history_group)
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(150)
        self.history_list.itemDoubleClicked.connect(self.load_from_history)
        history_layout.addWidget(self.history_list)
        
        history_controls = QHBoxLayout()
        self.clear_history_btn = QPushButton(self.tr("clear_history"))
        self.clear_history_btn.clicked.connect(self.clear_history)
        history_controls.addWidget(self.clear_history_btn)
        history_controls.addStretch()
        history_layout.addLayout(history_controls)
        
        right_panel.addWidget(self.history_group)
        
        # Layout'ları birleştir
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)
        
        # Menü çubuğu oluştur
        self.create_menu_bar()
        
        # Karanlık tema uygula
        self.apply_dark_theme()
        
        # Geçmişi yükle
        self.load_history()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Dosya menüsü
        self.file_menu = menubar.addMenu(self.tr("file_menu"))
        
        self.open_action = QAction(self.tr("open"), self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.triggered.connect(self.browse_input)
        self.file_menu.addAction(self.open_action)
        
        self.file_menu.addSeparator()
        
        # Dil menüsü
        self.language_menu = self.file_menu.addMenu(self.tr("language"))
        
        self.turkish_action = QAction(self.tr("turkish"), self)
        self.turkish_action.triggered.connect(lambda: self.change_language("tr"))
        self.language_menu.addAction(self.turkish_action)
        
        self.english_action = QAction(self.tr("english"), self)
        self.english_action.triggered.connect(lambda: self.change_language("en"))
        self.language_menu.addAction(self.english_action)
        
        self.file_menu.addSeparator()
        
        self.exit_action = QAction(self.tr("exit"), self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        # Yardım menüsü
        self.help_menu = menubar.addMenu(self.tr("help_menu"))
        
        self.about_action = QAction(self.tr("about"), self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)
    
    def change_language(self, lang):
        self.current_language = lang
        self.settings.setValue("language", lang)
        self.update_ui_texts()
    
    def update_ui_texts(self):
        # Ana pencere
        self.setWindowTitle(self.tr("window_title"))
        self.title_label.setText(self.tr("main_title"))
        
        # Dosya seçimi
        self.file_group.setTitle(self.tr("file_selection"))
        self.drop_area.setText(self.tr("drag_drop"))
        self.input_label.setText(self.tr("input"))
        self.output_label.setText(self.tr("output"))
        self.input_path.setPlaceholderText(self.tr("input_placeholder"))
        self.output_path.setPlaceholderText(self.tr("output_placeholder"))
        self.input_browse.setText(self.tr("browse"))
        self.output_browse.setText(self.tr("browse_output"))
        
        # Seçenekler
        self.options_group.setTitle(self.tr("anonymization_options"))
        self.method_label.setText(self.tr("method"))
        self.keep_audio.setText(self.tr("keep_audio"))
        self.preview_mode.setText(self.tr("preview_mode"))
        
        # Gelişmiş ayarlar
        self.advanced_group.setTitle(self.tr("advanced_settings"))
        self.threshold_label.setText(self.tr("detection_threshold"))
        self.mosaic_label.setText(self.tr("mosaic_size"))
        self.threshold_spin.setToolTip(self.tr("tooltip_threshold"))
        self.mosaic_size.setToolTip(self.tr("tooltip_mosaic_size"))
        
        # Tooltips
        self.method_combo.setItemData(0, self.tr("tooltip_blur"), Qt.ToolTipRole)
        self.method_combo.setItemData(1, self.tr("tooltip_mosaic"), Qt.ToolTipRole)
        self.method_combo.setItemData(2, self.tr("tooltip_solid"), Qt.ToolTipRole)
        
        # Butonlar
        self.process_btn.setText(self.tr("start_process"))
        self.clear_log_btn.setText(self.tr("clear"))
        self.save_log_btn.setText(self.tr("save"))
        self.clear_history_btn.setText(self.tr("clear_history"))
        
        # Gruplar
        self.log_group.setTitle(self.tr("process_log"))
        self.history_group.setTitle(self.tr("process_history"))
        
        # Menüler
        self.file_menu.setTitle(self.tr("file_menu"))
        self.help_menu.setTitle(self.tr("help_menu"))
        self.language_menu.setTitle(self.tr("language"))
        self.open_action.setText(self.tr("open"))
        self.turkish_action.setText(self.tr("turkish"))
        self.english_action.setText(self.tr("english"))
        self.exit_action.setText(self.tr("exit"))
        self.about_action.setText(self.tr("about"))
    
    def show_about(self):
        about_dialog = AboutDialog(self, self.current_language, self.translations)
        about_dialog.exec_()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.drop_area.setStyleSheet("""
                QLabel {
                    border: 2px dashed #0078d4;
                    border-radius: 8px;
                    background-color: #4c4c4c;
                    color: #ffffff;
                    font-size: 14px;
                }
            """)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 8px;
                background-color: #3c3c3c;
                color: #aaaaaa;
                font-size: 14px;
            }
        """)
    
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.input_path.setText(files[0])
            self.auto_suggest_output(files[0])
        self.dragLeaveEvent(event)
    
    def auto_suggest_output(self, input_path):
        if os.path.isfile(input_path):
            base, ext = os.path.splitext(input_path)
            self.output_path.setText(f"{base}_anonimlestirilmis{ext}")
        else:
            self.output_path.setText(input_path + "_anonimlestirilmis")
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.file_settings = json.load(f)
            else:
                self.file_settings = {"history": []}
        except:
            self.file_settings = {"history": []}
    
    def save_file_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.file_settings, f, indent=2)
        except:
            pass
    
    def load_history(self):
        self.history_list.clear()
        for item in self.file_settings.get("history", [])[-10:]:
            self.history_list.addItem(f"{item['date']} - {os.path.basename(item['input'])}")
    
    def add_to_history(self, input_path, output_path, method):
        history_item = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "input": input_path,
            "output": output_path,
            "method": method
        }
        
        if "history" not in self.file_settings:
            self.file_settings["history"] = []
        
        self.file_settings["history"].append(history_item)
        self.save_file_settings()
        self.load_history()
    
    def load_from_history(self, item):
        try:
            index = self.history_list.row(item)
            history_item = self.file_settings["history"][-(10-index)]
            self.input_path.setText(history_item["input"])
            self.output_path.setText(history_item["output"])
            method_index = ["blur", "mosaic", "solid"].index(history_item["method"])
            self.method_combo.setCurrentIndex(method_index)
        except:
            pass
    
    def clear_history(self):
        self.file_settings["history"] = []
        self.save_file_settings()
        self.load_history()
    
    def save_log(self):
        filename, _ = QFileDialog.getSaveFileName(self, self.tr("save_log_title"), "deface_log.txt", self.tr("text_files"))
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
            self.log_message(self.tr("log_saved"))
    
    def apply_dark_theme(self):
        dark_style = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QLineEdit {
            background-color: #3c3c3c;
            border: 2px solid #555555;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border-color: #0078d4;
        }
        QPushButton {
            background-color: #0078d4;
            border: none;
            border-radius: 6px;
            padding: 10px 15px;
            font-weight: bold;
            color: white;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #3c3c3c;
            border: 2px solid #555555;
            border-radius: 6px;
            padding: 6px;
            min-width: 80px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QCheckBox::indicator:unchecked {
            background-color: #3c3c3c;
            border: 2px solid #555555;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 2px solid #0078d4;
            border-radius: 3px;
        }
        QProgressBar {
            border: 2px solid #555555;
            border-radius: 6px;
            text-align: center;
            background-color: #3c3c3c;
        }
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 4px;
        }
        QTextEdit {
            background-color: #1e1e1e;
            border: 2px solid #555555;
            border-radius: 6px;
            padding: 8px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
        }
        QListWidget {
            background-color: #3c3c3c;
            border: 2px solid #555555;
            border-radius: 6px;
            padding: 4px;
        }
        QListWidget::item {
            padding: 4px;
            border-radius: 3px;
        }
        QListWidget::item:selected {
            background-color: #0078d4;
        }
        QLabel {
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_style)
        
    def browse_input(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter(self.tr("video_image_files"))
        
        if file_dialog.exec_():
            selected = file_dialog.selectedFiles()[0]
            self.input_path.setText(selected)
            self.auto_suggest_output(selected)
    
    def browse_output(self):
        input_path = self.input_path.text()
        if os.path.isfile(input_path):
            file_dialog = QFileDialog()
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            
            _, ext = os.path.splitext(input_path)
            if ext.lower() in ['.mp4', '.avi', '.mov']:
                file_dialog.setNameFilter(self.tr("video_files"))
            else:
                file_dialog.setNameFilter(self.tr("image_files"))
                
            if file_dialog.exec_():
                selected = file_dialog.selectedFiles()[0]
                if not os.path.splitext(selected)[1]:
                    selected += ext
                self.output_path.setText(selected)

            return
        
        self.process_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.log_text.clear()
        self.log_message(self.tr("process_starting"))
        
        # Geçmişe ekle
        self.add_to_history(
            self.input_path.text(),
            self.output_path.text(),
            self.method_combo.currentText()
        )
        
        # Worker başlat
        self.worker = ProcessWorker(
            self.input_path.text(),
            self.output_path.text(),
            self.method_combo.currentText(),
            self.keep_audio.isChecked(),
            self.preview_mode.isChecked(),

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(self.tr("success"))
            msg.setText(self.tr("process_success_msg"))
            msg.setInformativeText(self.tr("open_output_question"))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            
            if msg.exec_() == QMessageBox.Yes:
                if os.path.isfile(self.output_path.text()):
                    os.system(f'xdg-open "{os.path.dirname(self.output_path.text())}"')
                else:
                    os.system(f'xdg-open "{self.output_path.text()}"')
        else:
            self.log_message(self.tr("process_error").format(message))
            QMessageBox.critical(self, self.tr("error"), self.tr("process_failed").format(message))

class ProcessWorker(QThread):
    finished = pyqtSignal(bool, str)
    log_signal = pyqtSignal(str)
    
    def __init__(self, input_path, output_path, method, keep_audio, preview, threshold, mosaic_size, language, translations):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.method = method
        self.keep_audio = keep_audio
        self.preview = preview
        self.threshold = threshold
        self.mosaic_size = mosaic_size
        self.language = language
        self.translations = translations
    
    def tr(self, key):
        return self.translations[self.language].get(key, key)
    
   
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self.log_signal.emit(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.finished.emit(True, "")
            else:
                self.finished.emit(False, self.tr("process_failed_code").format(process.returncode))
                
        except FileNotFoundError:
            self.finished.emit(False, self.tr("deface_not_found"))
        except Exception as e:
            self.finished.emit(False, str(e))

class AboutDialog(QDialog):
    def __init__(self, parent=None, language="tr", translations=None):
        super().__init__(parent)
        self.language = language
        self.translations = translations
        
        self.setWindowTitle(self.tr("about_title"))
        self.setFixedSize(600, 700)
      
        # Ana scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo ve başlık
        title_layout = QVBoxLayout()
        
        # Logo
        logo = QLabel()
        icon_path = "/usr/share/pixmaps/defaceguilo.png"
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(scaled_pixmap)
        else:
            logo.setText("🎭")
            logo.setStyleSheet("font-size: 48px;")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(logo.styleSheet() + "margin-bottom: 10px;")
        title_layout.addWidget(logo)
        
        title = QLabel("Deface GUI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4; margin-bottom: 5px;")
        title_layout.addWidget(title)
        
        version = QLabel(self.tr("version"))
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("font-size: 14px; font-weight: bold; color: #0078d4; margin-bottom: 10px;")
        title_layout.addWidget(version)
        
        subtitle = QLabel(self.tr("about_subtitle"))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #888888; margin-bottom: 20px;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        
        # Özellikler
        features_group = QGroupBox(self.tr("features"))
        features_layout = QVBoxLayout(features_group)
        
        features_label = QLabel(self.tr("features_text"))
        features_label.setStyleSheet("padding: 10px; font-size: 11px; line-height: 1.4;")
        features_label.setWordWrap(True)
        features_layout.addWidget(features_label)
        
        layout.addWidget(features_group)
        
        # Geliştirici bilgileri
        dev_group = QGroupBox(self.tr("developer_info"))
        dev_layout = QVBoxLayout(dev_group)
        
        company_label = QLabel(self.tr("company"))
        company_label.setStyleSheet("padding: 3px; font-size: 12px;")
        dev_layout.addWidget(company_label)
        
        developer_label = QLabel(self.tr("developer"))
        developer_label.setStyleSheet("padding: 3px; font-size: 12px;")
        dev_layout.addWidget(developer_label)
        
        designer_label = QLabel(self.tr("designer"))
        designer_label.setStyleSheet("padding: 3px; font-size: 12px;")
        dev_layout.addWidget(designer_label)
        

        # Lisans bilgileri
        license_group = QGroupBox(self.tr("license_info"))
        license_layout = QVBoxLayout(license_group)
        
        license_label = QLabel(self.tr("license_text"))
        license_label.setStyleSheet("padding: 10px; font-size: 11px; line-height: 1.5;")
        license_label.setWordWrap(True)
        license_layout.addWidget(license_label)
        
        layout.addWidget(license_group)
        
        # Sorumluluk reddi
        disclaimer = QLabel(self.tr("disclaimer"))
        disclaimer.setAlignment(Qt.AlignCenter)
        disclaimer.setStyleSheet("""
            padding: 15px;
            font-size: 11px;
            font-weight: bold;
            color: #ff6b6b;
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 6px;
            margin: 10px 0;
        """)
        disclaimer.setWordWrap(True)
        layout.addWidget(disclaimer)
        
        # Scroll area'yı ayarla
        scroll.setWidget(content_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Kapat butonu ayrı olarak en altta
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 20)
        close_btn = QPushButton(self.tr("close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumHeight(35)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Dialog için karanlık tema
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QScrollArea {
                border: none;
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                background-color: #3c3c3c;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #0078d4;
            }
        """)
    
    def tr(self, key):
        return self.translations[self.language].get(key, key)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Deface GUI Enhanced")
    app.setOrganizationName("DefaceGUI")
    
    # Uygulama ikonu
    icon_path = "/usr/share/pixmaps/defaceguilo.png"
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = DefaceGUI()
    window.show()
    
    sys.exit(app.exec_())
