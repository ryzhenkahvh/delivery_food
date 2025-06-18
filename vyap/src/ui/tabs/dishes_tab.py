from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QGroupBox, QGridLayout, QHeaderView,
                             QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class DishesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        # Инициализация интерфейса вкладки блюд
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Группа ввода данных
        input_group = QGroupBox("Ввод данных")
        input_layout = QGridLayout()
        input_layout.setSpacing(10)
        
        # Поля ввода
        self.dish_name_input = QLineEdit()
        self.dish_name_input.setPlaceholderText("Введите название блюда")
        
        self.dish_category_combo = QComboBox()
        self.dish_category_combo.addItems(['Первое', 'Второе', 'Десерт', 'Напиток'])
        
        self.dish_price_input = QLineEdit()
        self.dish_price_input.setPlaceholderText("Введите цену")
        
        self.dish_cooking_time_input = QLineEdit()
        self.dish_cooking_time_input.setPlaceholderText("Введите время приготовления (мин)")
        
        # Размещение полей ввода
        input_layout.addWidget(QLabel("Название:"), 0, 0)
        input_layout.addWidget(self.dish_name_input, 0, 1)
        input_layout.addWidget(QLabel("Категория:"), 0, 2)
        input_layout.addWidget(self.dish_category_combo, 0, 3)
        input_layout.addWidget(QLabel("Цена:"), 1, 0)
        input_layout.addWidget(self.dish_price_input, 1, 1)
        input_layout.addWidget(QLabel("Время приготовления:"), 1, 2)
        input_layout.addWidget(self.dish_cooking_time_input, 1, 3)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Группа кнопок управления
        button_group = QGroupBox("Управление")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_button = QPushButton("Добавить")
        add_button.setIcon(QIcon.fromTheme("list-add"))
        add_button.clicked.connect(self.add_dish)
        
        update_button = QPushButton("Обновить")
        update_button.setIcon(QIcon.fromTheme("view-refresh"))
        update_button.clicked.connect(self.update_dish)
        
        delete_button = QPushButton("Удалить")
        delete_button.setIcon(QIcon.fromTheme("edit-delete"))
        delete_button.clicked.connect(self.delete_dish)
        
        refresh_button = QPushButton("Обновить список")
        refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_button.clicked.connect(self.refresh_data)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)
        
        # Таблица блюд
        self.dishes_table = QTableWidget()
        self.dishes_table.setColumnCount(5)
        self.dishes_table.setHorizontalHeaderLabels(['ID', 'Название', 'Категория', 'Цена', 'Время приготовления'])
        self.dishes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dishes_table.setAlternatingRowColors(True)
        self.dishes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dishes_table.setSelectionMode(QTableWidget.SingleSelection)
        self.dishes_table.itemSelectionChanged.connect(self.on_dish_select)
        layout.addWidget(self.dishes_table)

    def validate_inputs(self):
        # Валидация введенных данных
        name = self.dish_name_input.text().strip()
        price = self.dish_price_input.text().strip()
        cooking_time = self.dish_cooking_time_input.text().strip()
        
        # Проверка названия
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название блюда не может быть пустым")
            return False
        
        # Проверка цены
        if not price:
            QMessageBox.warning(self, "Ошибка", "Цена не может быть пустой")
            return False
        try:
            price_float = float(price.replace(',', '.'))
            if price_float < 0:
                QMessageBox.warning(self, "Ошибка", "Цена не может быть отрицательной")
                return False
            if price_float == 0:
                QMessageBox.warning(self, "Ошибка", "Цена должна быть больше нуля")
                return False
            # Обновляем поле цены с правильным форматом
            self.dish_price_input.setText(f"{price_float:.2f}")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть числом")
            return False
        
        # Проверка времени приготовления
        if not cooking_time:
            QMessageBox.warning(self, "Ошибка", "Время приготовления не может быть пустым")
            return False
        try:
            cooking_time_int = int(cooking_time)
            if cooking_time_int < 0:
                QMessageBox.warning(self, "Ошибка", "Время приготовления не может быть отрицательным")
                return False
            if cooking_time_int == 0:
                QMessageBox.warning(self, "Ошибка", "Время приготовления должно быть больше нуля")
                return False
            # Обновляем поле времени приготовления
            self.dish_cooking_time_input.setText(str(cooking_time_int))
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Время приготовления должно быть целым числом")
            return False
        
        return True

    def add_dish(self):
        # Добавление нового блюда
        if not self.validate_inputs():
            return
            
        name = self.dish_name_input.text().strip()
        category = self.dish_category_combo.currentText()
        price = float(self.dish_price_input.text())
        cooking_time = int(self.dish_cooking_time_input.text())
        
        try:
            self.db.add_dish(name, category, price, cooking_time)
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить блюдо: {str(e)}")

    def update_dish(self):
        # Обновление данных блюда
        if not self.validate_inputs():
            return
            
        selected_items = self.dishes_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите блюдо для обновления")
            return
        
        dish_id = int(self.dishes_table.item(selected_items[0].row(), 0).text())
        name = self.dish_name_input.text().strip()
        category = self.dish_category_combo.currentText()
        price = float(self.dish_price_input.text())
        cooking_time = int(self.dish_cooking_time_input.text())
        
        try:
            self.db.update_dish(dish_id, name, category, price, cooking_time)
            self.refresh_data()
            self.clear_inputs()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить блюдо: {str(e)}")

    def delete_dish(self):
        # Удаление блюда
        selected_items = self.dishes_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите блюдо для удаления")
            return
        
        dish_id = int(self.dishes_table.item(selected_items[0].row(), 0).text())
        
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   'Вы уверены, что хотите удалить это блюдо?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_dish(dish_id)
                self.refresh_data()
                self.clear_inputs()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить блюдо: {str(e)}")

    def refresh_data(self):
        # Обновление данных в таблице
        dishes = self.db.get_all_dishes()
        self.dishes_table.setRowCount(len(dishes))
        
        for i, dish in enumerate(dishes):
            self.dishes_table.setItem(i, 0, QTableWidgetItem(str(dish[0])))
            self.dishes_table.setItem(i, 1, QTableWidgetItem(dish[1]))
            self.dishes_table.setItem(i, 2, QTableWidgetItem(dish[2]))
            self.dishes_table.setItem(i, 3, QTableWidgetItem(str(dish[3])))
            self.dishes_table.setItem(i, 4, QTableWidgetItem(str(dish[4])))

    def on_dish_select(self):
        # Обработка выбора блюда в таблице
        selected_items = self.dishes_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.dish_name_input.setText(self.dishes_table.item(row, 1).text())
            self.dish_category_combo.setCurrentText(self.dishes_table.item(row, 2).text())
            self.dish_price_input.setText(self.dishes_table.item(row, 3).text())
            self.dish_cooking_time_input.setText(self.dishes_table.item(row, 4).text())

    def clear_inputs(self):
        # Очистка полей ввода
        self.dish_name_input.clear()
        self.dish_category_combo.setCurrentIndex(0)
        self.dish_price_input.clear()
        self.dish_cooking_time_input.clear() 