import sys
import os

# Добавляем путь к корневой директории проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from models.database import Database
from src.ui.main_window import MainWindow

def main():
    # Создание приложения
    app = QApplication(sys.argv)
    
    # Установка глобальных стилей шрифтов
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Инициализация базы данных
    db = Database()
    
    # Создание и отображение главного окна
    window = MainWindow()
    window.show()
    
    # Запуск приложения
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 