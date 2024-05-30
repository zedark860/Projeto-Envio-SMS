
import time
from PyQt5.QtCore import QThread, pyqtSignal
from twilio.rest import Client
from src.Classes.manipulacaoDados import ManipulacaoDados

class EnviosTwilio(QThread):
    log_message = pyqtSignal(str)
    sms_sent = pyqtSignal()
    sms_finished = pyqtSignal()
    
    def __init__(self, mensagem:str, account_sid:str, auth_token:str, to_number:str, min_time:int, max_time:int, spreadsheet) -> None:
        super().__init__()
        self.__mensagem:str = mensagem
        self.__account_sid:str = account_sid
        self.__auth_token:str = auth_token
        self.__to_number:str = to_number
        self.__min_time:int = min_time
        self.__max_time:int = max_time
        self.__spreadsheet = spreadsheet
        self.__contagem:int = 0
        
    @property
    def mensagem(self) -> str:
        return self.__mensagem
    
    @property
    def account_sid(self) -> str:
        return self.__account_sid
    
    @property
    def auth_token(self) -> str:
        return self.__auth_token
    
    @property
    def to_number(self) -> str:
        return self.__to_number
    
    @property
    def min_time(self) -> int:
        return self.__min_time
    
    @property
    def max_time(self) -> int:
        return self.__max_time
    
    def media_tempo(self) -> int:
        return (self.max_time + self.min_time) // 2
    
    def contagem_env(self) -> int:
        self.__contagem += 1
        log_message = f"Total de envios bem-sucedidos {self.__contagem}"
        self.log_message.emit(log_message)
        return self.__contagem
    
    def enviar_sms(self, client, from_number) -> str:
        client.messages.create(
            from_=self.__to_number,
            to=f"+{from_number}",
            body=self.__mensagem
        )

    def registrar_sucesso(self, manipulacao_dados, index, from_number):
        manipulacao_dados.registrarSucessoOuFalha(index, 'Sucesso', from_number)
        manipulacao_dados.registrarLogs()
        log_message = f"Envio bem-sucedido para o número: {from_number}\n"
        self.log_message.emit(log_message)

    def registrar_falha(self, manipulacao_dados, index, from_number, error):
        log_message = f"Erro ao enviar mensagem para o número: {from_number}\nErro: {error}\n"
        manipulacao_dados.registrarSucessoOuFalha(index, 'Falha', from_number)
        manipulacao_dados.registrarLogs()
        self.log_message.emit(log_message)  

    def run(self):
        client = Client(self.__account_sid, self.__auth_token)

        manipulacao_dados = ManipulacaoDados(self.__spreadsheet)

        for index, row in manipulacao_dados.df.iterrows():
            from_number = row["Números"]
            try:
                self.enviar_sms(client, from_number)
                self.registrar_sucesso(manipulacao_dados, index, from_number)
                self.contagem_env()
                time.sleep(self.media_tempo())
            except Exception as e:
                self.registrar_falha(manipulacao_dados, index, from_number, e)
                time.sleep(self.media_tempo())
                self.log_message.emit(f"Contagem de sucessos até o momento {self.__contagem}")
                continue
            finally:
                self.sms_finished.emit()