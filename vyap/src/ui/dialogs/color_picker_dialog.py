from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QColorDialog)
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal

class ColorPickerDialog(QDialog):
    color_changed = Signal(str)  # Сигнал для передачи выбранного цвета

    def __init__(self, parent=None, current_color="#0d47a1"):
        super().__init__(parent)
        self.current_color = current_color
        self.init_ui()

    def init_ui(self):
        # Инициализация интерфейса диалога
        self.setWindowTitle("Выбор цвета акцента")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Информационный текст
        info_label = QLabel("Выберите цвет акцента для приложения.\n"
                          "Этот цвет будет использоваться для кнопок,\n"
                          "выделений и других акцентных элементов.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Кнопка выбора цвета
        self.color_button = QPushButton("Выбрать цвет")
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(self.current_color)};
            }}
        """)
        self.color_button.clicked.connect(self.choose_color)
        layout.addWidget(self.color_button)

        # Кнопки управления
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("Применить")
        apply_button.clicked.connect(self.apply_color)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)

    def choose_color(self):
        # Открытие диалога выбора цвета
        color = QColorDialog.getColor(QColor(self.current_color), self, "Выберите цвет акцента")
        if color.isValid():
            self.current_color = color.name()
            self.color_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.current_color};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(self.current_color)};
                }}
            """)

    def apply_color(self):
        # Применение выбранного цвета
        self.color_changed.emit(self.current_color)
        self.accept()

    @staticmethod
    def lighten_color(color_hex):
        # Осветление цвета для эффекта наведения
        color = QColor(color_hex)
        h, s, v, a = color.getHsv()
        v = min(v + 20, 255)  # Увеличиваем яркость
        return QColor.fromHsv(h, s, v, a).name() 