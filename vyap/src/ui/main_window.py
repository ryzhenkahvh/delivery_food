from PySide6.QtWidgets import (QMainWindow, QTabWidget, QMessageBox, 
                             QMenuBar, QMenu)
from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QAction
import os
import json

from .tabs.dishes_tab import DishesTab
from .tabs.customers_tab import CustomersTab
from .tabs.orders_tab import OrdersTab
from .tabs.analytics_tab import AnalyticsTab
from .dialogs.color_picker_dialog import ColorPickerDialog
from ..models.database import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.db.create_tables()  # Теперь этот метод безопасно обновляет структуру БД
        self.is_dark_theme = False
        self.accent_color = "#0d47a1"  # Начальный цвет акцента
        self.load_settings()
        self.init_ui()
        
    def init_ui(self):
        # Инициализация пользовательского интерфейса
        self.setWindowTitle('Система управления доставкой еды')
        self.setGeometry(100, 100, 1200, 800)
        
        # Создание меню
        self.create_menu()
        
        # Создание вкладок
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Инициализация вкладок
        self.dishes_tab = DishesTab(self.db)
        self.customers_tab = CustomersTab(self.db)
        self.orders_tab = OrdersTab(self.db)
        self.analytics_tab = AnalyticsTab(self.db)
        
        # Добавление вкладок
        self.tab_widget.addTab(self.orders_tab, "Заказы")
        self.tab_widget.addTab(self.dishes_tab, "Блюда")
        self.tab_widget.addTab(self.customers_tab, "Клиенты")
        self.tab_widget.addTab(self.analytics_tab, "Аналитика")
        
        # Настройка таймера для автоматического обновления данных
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_tabs)
        self.refresh_timer.start(30000)  # Обновление каждые 30 секунд
        
        # Загрузка стилей
        self.load_styles()
    
    def create_menu(self):
        # Создание меню приложения
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')
        
        # Действие "Выход"
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Вид"
        view_menu = menubar.addMenu('Вид')
        
        # Действие "Тёмная тема"
        theme_action = QAction('Тёмная тема', self)
        theme_action.setCheckable(True)
        theme_action.setChecked(self.is_dark_theme)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Действие "Цвет акцента"
        color_action = QAction('Цвет акцента', self)
        color_action.triggered.connect(self.change_accent_color)
        view_menu.addAction(color_action)
    
    def toggle_theme(self, checked):
        # Переключение между светлой и тёмной темой
        self.is_dark_theme = checked
        self.load_styles()
        self.save_settings()
    
    def change_accent_color(self):
        # Изменение цвета акцента
        dialog = ColorPickerDialog(self, self.accent_color)
        dialog.color_changed.connect(self.set_accent_color)
        dialog.exec()
    
    def set_accent_color(self, color):
        # Установка нового цвета акцента
        self.accent_color = color
        self.load_styles()
        self.save_settings()
    
    def load_styles(self):
        # Загрузка стилей из QSS файла
        try:
            style_file = 'dark_theme.qss' if self.is_dark_theme else 'styles.qss'
            style_path = os.path.join(os.path.dirname(__file__), 'styles', style_file)
            with open(style_path, 'r', encoding='utf-8') as f:
                style = f.read()
                # Заменяем цвет акцента в стилях
                style = style.replace('#0d47a1', self.accent_color)
                style = style.replace('#1565c0', self.lighten_color(self.accent_color))
                style = style.replace('#0a3d91', self.darken_color(self.accent_color))
                self.setStyleSheet(style)
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")
    
    def load_settings(self):
        # Загрузка настроек из файла
        try:
            settings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.is_dark_theme = settings.get('dark_theme', False)
                    self.accent_color = settings.get('accent_color', '#0d47a1')
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        # Сохранение настроек в файл
        try:
            settings = {
                'dark_theme': self.is_dark_theme,
                'accent_color': self.accent_color
            }
            settings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    @staticmethod
    def lighten_color(color_hex):
        # Осветление цвета для эффекта наведения
        from PySide6.QtGui import QColor
        color = QColor(color_hex)
        h, s, v, a = color.getHsv()
        v = min(v + 20, 255)
        return QColor.fromHsv(h, s, v, a).name()
    
    @staticmethod
    def darken_color(color_hex):
        # Затемнение цвета для эффекта нажатия
        from PySide6.QtGui import QColor
        color = QColor(color_hex)
        h, s, v, a = color.getHsv()
        v = max(v - 20, 0)
        return QColor.fromHsv(h, s, v, a).name()
    
    def refresh_all_tabs(self):
        # Обновление данных на всех вкладках
        self.orders_tab.refresh_data()
        self.dishes_tab.refresh_data()
        self.customers_tab.refresh_data()
        self.analytics_tab.refresh_data()
    
    def closeEvent(self, event):
        # Обработка закрытия окна
        self.db.close()
        event.accept() 