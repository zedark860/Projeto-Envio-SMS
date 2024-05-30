
import webbrowser
import os
import sys
from queue import Queue
from PyQt5.QtWidgets import ( 
    QWidget, 
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QVBoxLayout, 
    QFileDialog, 
    QSpinBox,
    QTextEdit, 
    QHBoxLayout,
    QMessageBox,
    QCheckBox
    )
from PyQt5.QtCore import QThread, Qt

from src.styles.stylesMain import *
from src.Classes.enviosTwilio import EnviosTwilio

class TelaPrincipal(QWidget):
    
    @staticmethod
    def resource_path(relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(
            os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    
    def __init__(self) -> None:
        super().__init__()
        
        self.init_ui()
        self.sms_thread = None

    def init_ui(self) -> None:
        self.setWindowTitle("Envio de SMS")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet(styleMain)
        
        layout = QVBoxLayout()

        layout.addLayout(self._create_phone_number_field())
        layout.addLayout(self._create_account_sid())
        layout.addLayout(self._create_auth_token())
        layout.addLayout(self._create_spreadsheet_field())
        layout.addLayout(self._create_time_fields())
        layout.addLayout(self._create_message_field())
        layout.addLayout(self._create_buttons())
        
        self.log_output = QTextEdit()
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)
        
        self._gather_inputs()
        
    def _gather_inputs(self) -> None:
        self.inputs_queue = Queue()
        widgets:list = [
            self.phone_number_input,
            self.account_sid_input,
            self.account_sid_checkbox,
            self.auth_token_input,
            self.auth_token_checkbox,
            self.spreadsheet_input,
            self.browse_button,
            self.min_time_input,
            self.max_time_input,
            self.message_input,
            self.start_button
        ]
        for widget in widgets:
            self.inputs_queue.put(widget)
        
    def _disable_inputs_or_enable(self, enable:bool) -> None:
       size:int = self.inputs_queue.qsize()
       for _ in range(size):
           widget:bool = self.inputs_queue.get()
           widget.setEnabled(enable)
           self.inputs_queue.put(widget)

    def _create_phone_number_field(self):
        layout = QHBoxLayout()
        label = QLabel("Número de Telefone:")
        self.phone_number_input = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(self.phone_number_input)
        return layout
    
    def _toggle_password_visibility(self, state, line_edit):
        line_edit.setEchoMode(QLineEdit.Normal) if state == Qt.Checked else line_edit.setEchoMode(QLineEdit.Password)

    def _create_account_sid(self):
        layout = QHBoxLayout()
        label = QLabel("Seu Account Sid")
        self.account_sid_input = QLineEdit()
        self.account_sid_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(label)
        layout.addWidget(self.account_sid_input)
        
        self.account_sid_checkbox = QCheckBox("Mostrar")
        self.account_sid_checkbox.stateChanged.connect(lambda state: self._toggle_password_visibility(state, self.account_sid_input))
        layout.addWidget(self.account_sid_checkbox)

        return layout
            
    def _create_auth_token(self):
        layout = QHBoxLayout()
        label = QLabel("Seu Auth Token")
        self.auth_token_input = QLineEdit()
        self.auth_token_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(label)
        layout.addWidget(self.auth_token_input)

        self.auth_token_checkbox = QCheckBox("Mostrar")
        self.auth_token_checkbox.stateChanged.connect(lambda state: self._toggle_password_visibility(state, self.auth_token_input))
        layout.addWidget(self.auth_token_checkbox)

        return layout

    def _create_spreadsheet_field(self):
        layout = QHBoxLayout()
        label = QLabel("Planilha:")
        self.spreadsheet_input = QLineEdit()
        self.browse_button = QPushButton("Procurar")
        self.browse_button.clicked.connect(self._browse_file)
        layout.addWidget(label)
        layout.addWidget(self.spreadsheet_input)
        layout.addWidget(self.browse_button)
        return layout

    def _create_time_fields(self):
        layout = QHBoxLayout()
        
        min_time_label = QLabel("Tempo Mínimo (s):")
        self.min_time_input = QSpinBox()
        self.min_time_input.setMinimum(30)
        
        max_time_label = QLabel("Tempo Máximo (s):")
        self.max_time_input = QSpinBox()
        self.max_time_input.setMinimum(60)
        
        layout.addWidget(min_time_label)
        layout.addWidget(self.min_time_input)
        layout.addWidget(max_time_label)
        layout.addWidget(self.max_time_input)
        return layout

    def _create_message_field(self):
        layout = QVBoxLayout()
        label = QLabel("Mensagem:")
        self.message_input = QTextEdit()
        layout.addWidget(label)
        layout.addWidget(self.message_input)
        return layout

    def _create_buttons(self):
        layout = QHBoxLayout()
        self.start_button = QPushButton("Começar Envio")
        self.start_button.setStyleSheet(f"background-color: {cor_azul_escuro}")
        self.start_button.clicked.connect(self._start_sending)
        
        self.stop_button = QPushButton("Parar Envio")
        self.stop_button.clicked.connect(self._stop_sending)
        
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        return layout

    def _browse_file(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Escolher Planilha", "", "Todos os Arquivos (*);;Arquivos XLSX (*.xlsx)", options=options)
            if file_name:
                self.spreadsheet_input.setText(file_name)
        except Exception as e:
            self.update_log(f"Erro ao escolher arquivo: {e}")

    def _fields_are_filled(self) -> bool:
        try:
            fields = [
                self.phone_number_input,
                self.account_sid_input,
                self.auth_token_input,
                self.spreadsheet_input,
            ]
            
            for field in fields:
                if not field.text():
                    self.log_output.append("Por favor, preencha todos os campos.")
                    return False
                
            if not self.message_input.toPlainText():
                self.log_output.append("Por favor, preencha o campo de mensagem.")
                return False
                
            return True
        except Exception as e:
            self.update_log(f"Erro ao verificar campos: {e}")
            return False

    def _start_sending(self) -> None:
        try:
            if self._fields_are_filled():
                self._disable_inputs_or_enable(False)
                
                phone_number = self.phone_number_input.text()
                account_sid = self.account_sid_input.text()
                auth_token = self.auth_token_input.text()
                spreadsheet = self.spreadsheet_input.text()
                min_time = self.min_time_input.value()
                max_time = self.max_time_input.value()
                message = self.message_input.toPlainText()

                self.envios_twilio = EnviosTwilio(message, account_sid, auth_token, phone_number, min_time, max_time, spreadsheet)

                self.sms_thread = QThread()
                self.envios_twilio.moveToThread(self.sms_thread)
                
                self.envios_twilio.log_message.connect(self.update_log)
                self.envios_twilio.sms_finished.connect(self.sms_finished)
                self.sms_thread.started.connect(self.envios_twilio.run)
                self.sms_thread.start()
        except Exception as e:
            self.update_log(f"Erro ao iniciar envio: {e}")
            self._disable_inputs_or_enable(True)

    def _stop_sending(self) -> None:
        try:
            if self.sms_thread and self.sms_thread.isRunning():
                self.sms_thread.terminate()
                self.sms_thread.wait()
                self._disable_inputs_or_enable(True)
                QMessageBox.information(self, 'Envio interrompido.', 'Envio de SMS interrompido!')
        except Exception as e:
            self.update_log(f"Erro ao interromper envio: {e}")

    def update_log(self, message:str) -> None:
        self.log_output.append(message)

    def sms_finished(self) -> None:
        self._disable_inputs_or_enable(True)
        QMessageBox.information(self, 'Envio Concluído', 'Todos os SMS foram enviados com sucesso!')
