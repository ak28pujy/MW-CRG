import asyncio
import os
import sys

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QComboBox, QGroupBox, QFormLayout
from dotenv import load_dotenv, set_key

from main import main

load_dotenv()

BUTTON_STYLE = "background-color: #4CAF50; font-size: 12px; color: white;"


def create_input_line(env_variable):
    return QtWidgets.QLineEdit(os.getenv(env_variable))


def create_scrollable_input(env_variable):
    text_edit = QtWidgets.QTextEdit()
    text_edit.setPlainText(os.getenv(env_variable))
    text_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    text_edit.setMaximumHeight(60)
    return text_edit


class SettingsWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.value1_input = None
        self.value2_input = None
        self.value3_input = None
        self.value4_input = None
        self.value5_input = None
        self.value6_input = None
        self.setWindowTitle('Settings')
        self.initialize_inputs()
        self.initialize_layout()

    def initialize_inputs(self):
        self.value1_input = create_input_line('OPENAI_API_KEY')
        self.value2_input = create_input_line('GOOGLE_API_KEY')
        self.value3_input = create_input_line('GOOGLE_CSE_ID')
        self.value4_input = create_input_line('MAX_CONCURRENT_TASKS')
        self.value5_input = create_input_line('MAX_CONCURRENT_URLS')
        self.value6_input = create_input_line('PAGE_LOAD_TIMEOUT')

    def initialize_layout(self):
        layout = QtWidgets.QVBoxLayout()
        form_layout = self.create_form_layout()

        save_button = self.create_save_button()

        layout.addLayout(form_layout)
        layout.addWidget(save_button)
        self.setLayout(layout)
        self.setStyleSheet("font-size: 12px;")

    def create_form_layout(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("OPENAI API KEY:", self.value1_input)
        form_layout.addRow("GOOGLE API KEY:", self.value2_input)
        form_layout.addRow("GOOGLE CSE ID:", self.value3_input)
        form_layout.addRow("MAX CONCURRENT TASKS:", self.value4_input)
        form_layout.addRow("MAX CONCURRENT URLS:", self.value5_input)
        form_layout.addRow("PAGE LOAD TIMEOUT (in sec.):", self.value6_input)
        return form_layout

    def create_save_button(self):
        save_button = QtWidgets.QPushButton('Save', self)
        save_button.setStyleSheet(BUTTON_STYLE)
        save_button.clicked.connect(self.save_values)
        return save_button

    def save_values(self):
        set_key('.env', 'OPENAI_API_KEY', self.value1_input.text())
        set_key('.env', 'GOOGLE_API_KEY', self.value2_input.text())
        set_key('.env', 'GOOGLE_CSE_ID', self.value3_input.text())
        set_key('.env', 'MAX_CONCURRENT_TASKS', self.value4_input.text())
        set_key('.env', 'MAX_CONCURRENT_URLS', self.value5_input.text())
        set_key('.env', 'PAGE_LOAD_TIMEOUT', self.value6_input.text())
        QtWidgets.QMessageBox.information(self, "Saved", "The settings have been saved.")
        self.close()


class InfoWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initialize_layout()

    def initialize_layout(self):
        self.setWindowTitle('Information')
        layout = QtWidgets.QVBoxLayout()
        info_label = QtWidgets.QLabel("Information about the program...")
        layout.addWidget(info_label)

        ok_button = QtWidgets.QPushButton('OK', self)
        ok_button.setStyleSheet(BUTTON_STYLE)
        ok_button.clicked.connect(self.close)

        layout.addWidget(ok_button)
        self.setLayout(layout)
        self.setStyleSheet("font-size: 12px;")


class EmittingStream(QtCore.QObject):
    text_written = pyqtSignal(str, name="text_written")

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass


class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.info_window = None
        self.settings_window = None
        self.setWindowTitle('Company Report Generator')
        self.setFixedSize(500, 750)

        self.init_ui()
        self.central_widget = MyWidget()
        self.setCentralWidget(self.central_widget)
        self.setStyleSheet("QGroupBox { border: 1px solid gray; border-radius: 5px; margin-top: 10px; } "
                           "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")

    def init_ui(self):
        menubar = self.menuBar()
        self.menuBar().setNativeMenuBar(False)
        menu = menubar.addMenu('Menu')

        settings_action = QtGui.QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)

        info_action = QtGui.QAction('Info', self)
        info_action.triggered.connect(self.open_info)
        menu.addAction(info_action)

    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def open_info(self):
        self.info_window = InfoWindow()
        self.info_window.show()


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.company_input = None
        self.search_terms_google_search_input = None
        self.search_terms_google_news_input = None
        self.num_urls_google_search_input = None
        self.num_urls_google_news_input = None
        self.model_dropdown = None
        self.language_dropdown = None
        self.prompt_as_txt_checkbox = None
        self.report_as_txt_checkbox = None
        self.report_as_pdf_checkbox = None
        self.log_console = None
        self.main_thread = None
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.setFixedHeight(20)
        self.status_bar.showMessage("Ready...")
        self.initialize_inputs()
        self.initialize_layout()

    def initialize_inputs(self):
        self.company_input = create_input_line('COMPANY_NAME')
        self.search_terms_google_search_input = create_scrollable_input('SEARCH_TERMS_GOOGLE_SEARCH')
        self.search_terms_google_news_input = create_scrollable_input('SEARCH_TERMS_GOOGLE_NEWS')
        self.num_urls_google_search_input = QtWidgets.QSpinBox(self)
        self.num_urls_google_search_input.valueChanged.connect(self.max_google_search_urls)
        self.num_urls_google_news_input = QtWidgets.QSpinBox(self)
        self.num_urls_google_news_input.valueChanged.connect(self.max_google_news_urls)
        self.model_dropdown = QComboBox(self)
        self.language_dropdown = QComboBox(self)
        self.log_console = QtWidgets.QPlainTextEdit(self)
        self.prompt_as_txt_checkbox = QtWidgets.QCheckBox("Prompt as TXT", self)
        self.report_as_txt_checkbox = QtWidgets.QCheckBox("Report as TXT", self)
        self.report_as_pdf_checkbox = QtWidgets.QCheckBox("Report as PDF", self)

        self.set_default_values()

    def set_default_values(self):
        self.num_urls_google_search_input.setValue(5)
        self.num_urls_google_news_input.setValue(10)
        self.model_dropdown.addItems(["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"])
        self.model_dropdown.setCurrentIndex(1)
        self.language_dropdown.addItems(["English", "German", "French"])
        self.language_dropdown.setCurrentIndex(1)
        self.log_console.setReadOnly(True)
        self.prompt_as_txt_checkbox.setChecked(True)
        self.report_as_txt_checkbox.setChecked(True)
        self.report_as_pdf_checkbox.setChecked(True)

    def max_google_search_urls(self):
        if self.num_urls_google_search_input.value() > 10:
            self.num_urls_google_search_input.setValue(10)

    def max_google_news_urls(self):
        if self.num_urls_google_news_input.value() > 20:
            self.num_urls_google_news_input.setValue(20)

    def initialize_layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.create_company_group())
        layout.addWidget(self.create_search_group())
        layout.addWidget(self.create_urls_group())
        layout.addWidget(self.create_model_group())
        layout.addWidget(self.create_output_group())
        layout.addWidget(self.log_console)
        layout.addWidget(self.status_bar)
        layout.addWidget(self.create_generate_button())
        self.setLayout(layout)

    def create_company_group(self):
        company_group = QGroupBox("Company")
        company_layout = QFormLayout()
        company_layout.addRow(self.company_input)
        company_group.setLayout(company_layout)
        return company_group

    def create_search_group(self):
        search_group = QGroupBox("Search Terms")
        search_layout = QFormLayout()
        search_layout.addRow("Google Search:", self.search_terms_google_search_input)
        search_layout.addRow("Google News:", self.search_terms_google_news_input)
        search_group.setLayout(search_layout)
        return search_group

    def create_urls_group(self):
        urls_group = QGroupBox("Number of URLs")
        urls_layout = QFormLayout()
        urls_layout.addRow("Google Search:", self.num_urls_google_search_input)
        urls_layout.addRow("Google News:", self.num_urls_google_news_input)
        urls_group.setLayout(urls_layout)
        return urls_group

    def create_model_group(self):
        model_group = QGroupBox("Model && Language")
        model_layout = QFormLayout()
        model_layout.addRow("Model:", self.model_dropdown)
        model_layout.addRow("Language:", self.language_dropdown)
        model_group.setLayout(model_layout)
        return model_group

    def create_output_group(self):
        output_group = QGroupBox("Output")
        output_layout = QtWidgets.QVBoxLayout()
        output_layout.addWidget(self.prompt_as_txt_checkbox)
        output_layout.addWidget(self.report_as_txt_checkbox)
        output_layout.addWidget(self.report_as_pdf_checkbox)
        output_group.setLayout(output_layout)
        return output_group

    def create_generate_button(self):
        generate_button = QtWidgets.QPushButton('Generate Report', self)
        generate_button.setStyleSheet(BUTTON_STYLE)
        generate_button.clicked.connect(self.generate_report)
        return generate_button

    def add_log(self, message):
        self.log_console.appendPlainText(message)
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def stop_loading(self):
        self.status_bar.showMessage("Ready...")
        QtWidgets.QMessageBox.information(self, "Finished", "The report was successfully created.")

    def generate_report(self):
        company = self.company_input.text().strip()
        search_terms_google_search = self.search_terms_google_search_input.toPlainText().strip()
        search_terms_google_news = self.search_terms_google_news_input.toPlainText().strip()
        model = self.model_dropdown.currentText()
        language = self.language_dropdown.currentText()
        num_urls_google_search = self.num_urls_google_search_input.value()
        num_urls_google_news = self.num_urls_google_news_input.value()
        prompt_as_txt = self.prompt_as_txt_checkbox.isChecked()
        report_as_txt = self.report_as_txt_checkbox.isChecked()
        report_as_pdf = self.report_as_pdf_checkbox.isChecked()

        if not company:
            QtWidgets.QMessageBox.warning(self, "Error", "The Company field must not be empty.")
            return

        set_key('.env', 'COMPANY_NAME', company)
        set_key('.env', 'SEARCH_TERMS_GOOGLE_SEARCH', search_terms_google_search)
        set_key('.env', 'SEARCH_TERMS_GOOGLE_NEWS', search_terms_google_news)
        search_terms_google_search = search_terms_google_search.split(',') if search_terms_google_search else []
        search_terms_google_news = search_terms_google_news.split(',') if search_terms_google_news else []

        self.status_bar.showMessage("Loading...")
        self.main_thread = MainThread(company, search_terms_google_search, search_terms_google_news, model, language,
                                      num_urls_google_search, num_urls_google_news, prompt_as_txt, report_as_txt,
                                      report_as_pdf)
        self.main_thread.log_signal.connect(self.add_log)
        self.main_thread.finished.connect(self.stop_loading)
        self.main_thread.start()


class MainThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, company, search_terms_google_search, search_terms_google_news, model, language,
                 num_urls_google_search, num_urls_google_news, prompt_as_txt, report_as_txt, report_as_pdf):
        super().__init__()
        self.company = company
        self.search_terms_google_search = search_terms_google_search
        self.search_terms_google_news = search_terms_google_news
        self.model = model
        self.language = language
        self.num_urls_google_search = num_urls_google_search
        self.num_urls_google_news = num_urls_google_news
        self.prompt_as_txt = prompt_as_txt
        self.report_as_txt = report_as_txt
        self.report_as_pdf = report_as_pdf

    def run(self):
        stream = EmittingStream()
        stream.text_written.connect(self.log_signal.emit)
        sys.stdout = stream

        asyncio.run(main(self.company, self.search_terms_google_search, self.search_terms_google_news, self.model,
                         self.language, self.num_urls_google_search, self.num_urls_google_news, self.prompt_as_txt,
                         self.report_as_txt, self.report_as_pdf))

        sys.stdout = sys.__stdout__


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MyApp()
    window.show()
    sys.exit(app.exec())