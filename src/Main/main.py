import sys
from PyQt5.QtWidgets import QApplication
from controller import Controller  # Importar el controlador desde el mismo directorio
from main_window_ui import Ui_MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show()
    sys.exit(app.exec_())
