from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QGroupBox, QGridLayout, QHeaderView, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import re

class CustomersTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        # Инициализация интерфейса вкладки клиентов
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Группа ввода данных
        input_group = QGroupBox("Ввод данных")
        input_layout = QGridLayout()
        input_layout.setSpacing(10)
        
        # Поля ввода
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Введите имя")
        
        self.customer_address_input = QLineEdit()
        self.customer_address_input.setPlaceholderText("Введите адрес")
        
        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setPlaceholderText("Введите телефон")
        
        self.customer_email_input = QLineEdit()
        self.customer_email_input.setPlaceholderText("Введите email")
        
        # Размещение полей ввода
        input_layout.addWidget(QLabel("Имя:"), 0, 0)
        input_layout.addWidget(self.customer_name_input, 0, 1)
        input_layout.addWidget(QLabel("Адрес:"), 0, 2)
        input_layout.addWidget(self.customer_address_input, 0, 3)
        input_layout.addWidget(QLabel("Телефон:"), 1, 0)
        input_layout.addWidget(self.customer_phone_input, 1, 1)
        input_layout.addWidget(QLabel("Email:"), 1, 2)
        input_layout.addWidget(self.customer_email_input, 1, 3)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Группа кнопок управления
        button_group = QGroupBox("Управление")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_button = QPushButton("Добавить")
        add_button.setIcon(QIcon.fromTheme("list-add"))
        add_button.clicked.connect(self.add_customer)
        
        update_button = QPushButton("Обновить")
        update_button.setIcon(QIcon.fromTheme("view-refresh"))
        update_button.clicked.connect(self.update_customer)
        
        delete_button = QPushButton("Удалить")
        delete_button.setIcon(QIcon.fromTheme("edit-delete"))
        delete_button.clicked.connect(self.delete_customer)
        
        refresh_button = QPushButton("Обновить список")
        refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_button.clicked.connect(self.refresh_data)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)
        
        # Таблица клиентов
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(5)
        self.customers_table.setHorizontalHeaderLabels(['ID', 'Имя', 'Адрес', 'Телефон', 'Email'])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customers_table.itemSelectionChanged.connect(self.on_customer_select)
        layout.addWidget(self.customers_table)

    def validate_inputs(self):
        # Валидация введенных данных
        name = self.customer_name_input.text().strip()
        address = self.customer_address_input.text().strip()
        phone = self.customer_phone_input.text().strip()
        email = self.customer_email_input.text().strip()
        
        # Проверка имени
        if not name:
            QMessageBox.warning(self, "Ошибка", "Имя не может быть пустым")
            return False
        
        # Проверка адреса
        if not address:
            QMessageBox.warning(self, "Ошибка", "Адрес не может быть пустым")
            return False
        
        # Проверка телефона
        if phone:
            # Удаляем все нецифровые символы
            phone_digits = re.sub(r'\D', '', phone)
            if not phone_digits.isdigit():
                QMessageBox.warning(self, "Ошибка", "Телефон должен содержать только цифры")
                return False
            if len(phone_digits) < 10:
                QMessageBox.warning(self, "Ошибка", "Телефон должен содержать минимум 10 цифр")
                return False
            if len(phone_digits) > 15:
                QMessageBox.warning(self, "Ошибка", "Телефон не может содержать более 15 цифр")
                return False
            # Обновляем поле телефона, оставляя только цифры
            self.customer_phone_input.setText(phone_digits)
        
        # Проверка email
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                QMessageBox.warning(self, "Ошибка", "Некорректный формат email")
                return False
        
        return True

    def add_customer(self):
        # Добавление нового клиента
        if not self.validate_inputs():
            return
            
        name = self.customer_name_input.text().strip()
        address = self.customer_address_input.text().strip()
        phone = self.customer_phone_input.text().strip()
        email = self.customer_email_input.text().strip()
        
        try:
            self.db.add_customer(name, address, phone, email)
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            if 'уже существует' in str(e):
                QMessageBox.warning(self, "Дубликат клиента", "Клиент с такими данными уже существует!")
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить клиента: {str(e)}")

    def update_customer(self):
        # Обновление данных клиента
        if not self.validate_inputs():
            return
            
        selected_items = self.customers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента для обновления")
            return
        
        customer_id = int(self.customers_table.item(selected_items[0].row(), 0).text())
        name = self.customer_name_input.text().strip()
        address = self.customer_address_input.text().strip()
        phone = self.customer_phone_input.text().strip()
        email = self.customer_email_input.text().strip()
        
        try:
            self.db.update_customer(customer_id, name, address, phone, email)
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить клиента: {str(e)}")

    def delete_customer(self):
        # Удаление клиента
        selected_items = self.customers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента для удаления")
            return
        
        customer_id = int(self.customers_table.item(selected_items[0].row(), 0).text())
        
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   'Вы уверены, что хотите удалить этого клиента?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_customer(customer_id)
                self.refresh_data()
                self.clear_inputs()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить клиента: {str(e)}")

    def refresh_data(self):
        # Обновление данных в таблице
        customers = self.db.get_all_customers()
        self.customers_table.setRowCount(len(customers))
        
        for i, customer in enumerate(customers):
            for j, value in enumerate(customer):
                self.customers_table.setItem(i, j, QTableWidgetItem(str(value)))

    def on_customer_select(self):
        # Обработка выбора клиента в таблице
        selected_items = self.customers_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.customer_name_input.setText(self.customers_table.item(row, 1).text())
            self.customer_address_input.setText(self.customers_table.item(row, 2).text())
            self.customer_phone_input.setText(self.customers_table.item(row, 3).text())
            self.customer_email_input.setText(self.customers_table.item(row, 4).text())

    def clear_inputs(self):
        # Очистка полей ввода
        self.customer_name_input.clear()
        self.customer_address_input.clear()
        self.customer_phone_input.clear()
        self.customer_email_input.clear() 