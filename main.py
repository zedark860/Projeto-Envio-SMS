
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.telaPrincipal import TelaPrincipal

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    tela_principal = TelaPrincipal()
    
    icon_path = tela_principal.resource_path(os.path.join("img", "icon.ico"))
    
    app_icon = QIcon(icon_path)
    tela_principal.setWindowIcon(app_icon)
    
    tela_principal.show()
    
    sys.exit(app.exec_())
