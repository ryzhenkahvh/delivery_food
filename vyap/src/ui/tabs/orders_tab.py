from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QGroupBox, QGridLayout, QHeaderView,
                             QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import re
import datetime

class OrdersTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        # Инициализация интерфейса вкладки заказов
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Группа ввода данных
        input_group = QGroupBox("Ввод данных")
        input_layout = QGridLayout()
        input_layout.setSpacing(10)
        
        # Поля ввода
        self.order_customer_combo = QComboBox()
        self.order_customer_combo.setPlaceholderText("Выберите клиента")
        
        self.order_dish_combo = QComboBox()
        self.order_dish_combo.setPlaceholderText("Выберите блюдо")
        
        self.order_status_combo = QComboBox()
        self.order_status_combo.addItems(['Новый', 'В обработке', 'В доставке', 'Завершен'])
        
        # Размещение полей ввода
        input_layout.addWidget(QLabel("Клиент:"), 0, 0)
        input_layout.addWidget(self.order_customer_combo, 0, 1)
        input_layout.addWidget(QLabel("Блюдо:"), 0, 2)
        input_layout.addWidget(self.order_dish_combo, 0, 3)
        input_layout.addWidget(QLabel("Статус:"), 1, 0)
        input_layout.addWidget(self.order_status_combo, 1, 1)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Группа кнопок управления
        button_group = QGroupBox("Управление")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_button = QPushButton("Добавить")
        add_button.setIcon(QIcon.fromTheme("list-add"))
        add_button.clicked.connect(self.add_order)
        
        update_button = QPushButton("Обновить")
        update_button.setIcon(QIcon.fromTheme("view-refresh"))
        update_button.clicked.connect(self.update_order)
        
        delete_button = QPushButton("Удалить")
        delete_button.setIcon(QIcon.fromTheme("edit-delete"))
        delete_button.clicked.connect(self.delete_order)
        
        refresh_button = QPushButton("Обновить список")
        refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_button.clicked.connect(self.refresh_data)
        
        export_button = QPushButton("Экспорт в CSV")
        export_button.setIcon(QIcon.fromTheme("document-save"))
        export_button.clicked.connect(self.export_to_csv)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(export_button)
        
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)
        
        # Таблица заказов
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(10)
        self.orders_table.setHorizontalHeaderLabels([
            'ID', 'Клиент', 'Блюдо', 'Статус', 'Дата',
            'Адрес', 'Телефон', 'Категория', 'Цена', 'Время приготовления'
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setSelectionMode(QTableWidget.SingleSelection)
        self.orders_table.itemSelectionChanged.connect(self.on_order_select)
        layout.addWidget(self.orders_table)

    def add_order(self):
        # Добавление нового заказа
        customer_id = self.get_selected_customer_id()
        dish_id = self.get_selected_dish_id()
        status = self.order_status_combo.currentText()
        
        if customer_id and dish_id:
            self.db.add_order(customer_id, dish_id, status)
            self.refresh_data()
            self.clear_inputs()

    def update_order(self):
        # Обновление выбранного заказа
        selected = self.orders_table.selectedItems()
        if not selected:
            return
            
        order_id = int(self.orders_table.item(selected[0].row(), 0).text())
        customer_id = self.get_selected_customer_id()
        dish_id = self.get_selected_dish_id()
        status = self.order_status_combo.currentText()
        
        if customer_id and dish_id:
            self.db.update_order(order_id, customer_id, dish_id, status)
            self.refresh_data()
            self.clear_inputs()

    def delete_order(self):
        # Удаление выбранного заказа
        selected = self.orders_table.selectedItems()
        if not selected:
            return
            
        order_id = int(self.orders_table.item(selected[0].row(), 0).text())
        self.db.delete_order(order_id)
        self.refresh_data()
        self.clear_inputs()

    def refresh_data(self):
        # Обновление данных в таблице и комбобоксах
        # Обновление списка клиентов
        self.order_customer_combo.clear()
        customers = self.db.get_all_customers()
        for customer in customers:
            self.order_customer_combo.addItem(customer[1], customer[0])
        
        # Обновление списка блюд
        self.order_dish_combo.clear()
        dishes = self.db.get_all_dishes()
        for dish in dishes:
            self.order_dish_combo.addItem(dish[1], dish[0])
        
        # Обновление таблицы заказов
        orders = self.db.get_all_orders()
        self.orders_table.setRowCount(len(orders))
        
        for i, order in enumerate(orders):
            for j, value in enumerate(order):
                self.orders_table.setItem(i, j, QTableWidgetItem(str(value)))

    def on_order_select(self):
        # Обработчик выбора заказа в таблице
        selected = self.orders_table.selectedItems()
        if not selected:
            return
        
        # Получение данных выбранного заказа
        customer_name = self.orders_table.item(selected[0].row(), 1).text()
        dish_name = self.orders_table.item(selected[0].row(), 2).text()
        status = self.orders_table.item(selected[0].row(), 3).text()
        
        # Установка значений в комбобоксы
        index = self.order_customer_combo.findText(customer_name)
        if index >= 0:
            self.order_customer_combo.setCurrentIndex(index)
            
        index = self.order_dish_combo.findText(dish_name)
        if index >= 0:
            self.order_dish_combo.setCurrentIndex(index)
            
        index = self.order_status_combo.findText(status)
        if index >= 0:
            self.order_status_combo.setCurrentIndex(index)

    def get_selected_customer_id(self):
        # Получение ID выбранного клиента
        return self.order_customer_combo.currentData()

    def get_selected_dish_id(self):
        # Получение ID выбранного блюда
        return self.order_dish_combo.currentData()

    def clear_inputs(self):
        # Очистка полей ввода
        self.order_customer_combo.setCurrentIndex(-1)
        self.order_dish_combo.setCurrentIndex(-1)
        self.order_status_combo.setCurrentIndex(0)

    def export_to_csv(self):
        # Экспорт заказов в CSV с датой в формате ДД.ММ.ГГГГ (так и не понял, как сделать дату в формате ДД.ММ.ГГГГ)
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить как CSV",
                f"orders_{datetime.datetime.now().strftime('%d%m%Y_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            if not filename:
                return
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                headers = [self.orders_table.horizontalHeaderItem(i).text() for i in range(self.orders_table.columnCount())]
                f.write(';'.join(headers) + '\n')
                date_pattern = re.compile(r'^(\d{4})-(\d{2})-(\d{2})')
                for row in range(self.orders_table.rowCount()):
                    row_data = []
                    for col in range(self.orders_table.columnCount()):
                        item = self.orders_table.item(row, col)
                        text = item.text() if item else ''
                        # Форматируем только колонку "Дата" (индекс 4)
                        if col == 4:
                            match = date_pattern.match(text)
                            if match:
                                text = f"{match.group(3)}.{match.group(2)}.{match.group(1)}"
                        row_data.append(text)
                    f.write(';'.join(row_data) + '\n')
            QMessageBox.information(self, "Экспорт завершён", f"Данные успешно экспортированы в файл:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Ошибка при экспорте в CSV: {e}") 