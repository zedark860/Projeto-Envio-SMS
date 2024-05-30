
import pandas as pd
import os
import sys
from datetime import datetime

class ManipulacaoDados:
    
    @staticmethod
    def resource_path(relative_path) -> os.path.join:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    
    @staticmethod
    def horaAtual() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __init__(self, filename:str) -> None:
        self.filename:str = filename
        self._df = None
        
    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self.leituraDados()
        return self._df
        
    def leituraDados(self) -> None:
        try:
            filepath = self.resource_path(self.filename)
            self._df = pd.read_excel(filepath)
            self._df['Números'] = self._df['Números'].astype(str).apply(lambda x: x.split('.')[0])
        except FileNotFoundError:
            raise FileNotFoundError(f"Erro: Arquivo não encontrado em {self.filename}")
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo: {e}")
    
    def registrarSucessoOuFalha(self, index, status, number) -> None:
        self._df['STATUS'] = self._df['STATUS'].astype('object')
        self._df.at[index, 'STATUS'] = status
        self.registrarSucessoOuFalhaTXT(status, number)   
        
    def registrarSucessoOuFalhaTXT(self, status, number):
        arquivo_sucesso = self.resource_path("../logs/logsSucessoOuFalha.txt")
        
        if not os.path.exists(arquivo_sucesso):
            os.makedirs(os.path.dirname(arquivo_sucesso), exist_ok=True)
            
        with open(arquivo_sucesso, 'a') as file:
            file.write(f"{self.horaAtual()} {number} {status}\n")
    
    def registrarLogs(self) -> None:
        try:
            filepath = self.resource_path(self.filename)
            self._df.to_excel(filepath, index=False)
        except Exception as e:
            raise Exception(f"Erro ao salvar arquivo: {e}")