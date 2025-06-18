from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QGroupBox, QGridLayout, QHeaderView,
                             QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import csv
import datetime
import re
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class AnalyticsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        # Инициализация интерфейса вкладки аналитики
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Группа фильтров
        filter_group = QGroupBox("Фильтры")
        filter_layout = QGridLayout()
        filter_layout.setSpacing(10)
        
        # Фильтры
        self.period_combo = QComboBox()
        self.period_combo.addItems(['Все время', 'За день', 'За неделю', 'За месяц'])
        self.period_combo.currentTextChanged.connect(self.refresh_data)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(['Все категории'])
        self.category_combo.currentTextChanged.connect(self.refresh_data)
        
        # Размещение фильтров
        filter_layout.addWidget(QLabel("Период:"), 0, 0)
        filter_layout.addWidget(self.period_combo, 0, 1)
        filter_layout.addWidget(QLabel("Категория:"), 0, 2)
        filter_layout.addWidget(self.category_combo, 0, 3)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # --- добавим график ---
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        # --- конец блока графика ---
        
        # Группа кнопок экспорта
        export_group = QGroupBox("Экспорт данных")
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        
        csv_button = QPushButton("Экспорт в CSV")
        csv_button.setIcon(QIcon.fromTheme("document-save"))
        csv_button.clicked.connect(self.export_to_csv)
        
        html_button = QPushButton("Экспорт в HTML")
        html_button.setIcon(QIcon.fromTheme("document-save"))
        html_button.clicked.connect(self.export_to_html)
        
        refresh_button = QPushButton("Обновить данные")
        refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_button.clicked.connect(self.refresh_data)
        
        export_layout.addWidget(csv_button)
        export_layout.addWidget(html_button)
        export_layout.addWidget(refresh_button)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Таблица аналитики
        self.analytics_table = QTableWidget()
        self.analytics_table.setColumnCount(9)
        self.analytics_table.setHorizontalHeaderLabels([
            'ID', 'Название', 'Категория', 'Количество заказов',
            'Общая сумма', 'Средняя цена', 'Мин. цена', 'Макс. цена',
            'Ср. время приготовления'
        ])
        self.analytics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.analytics_table.setAlternatingRowColors(True)
        layout.addWidget(self.analytics_table)

    def refresh_data(self):
        # Обновление данных в таблице и графике
        # Получение периода
        period = self.period_combo.currentText()
        date_from = None
        
        if period == 'За день':
            date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        elif period == 'За неделю':
            date_from = datetime.datetime.now() - datetime.timedelta(weeks=1)
        elif period == 'За месяц':
            date_from = datetime.datetime.now() - datetime.timedelta(days=30)
        
        # Получение статистики
        stats = self.db.get_order_statistics(date_from)
        filtered_stats = []
        
        for stat in stats.values():
            # Фильтр по категории
            if (self.category_combo.currentText() == 'Все категории' or 
                stat['category'] == self.category_combo.currentText()):
                filtered_stats.append(stat)
        
        # Обновление таблицы
        self.analytics_table.setRowCount(len(filtered_stats))
        for i, stat in enumerate(filtered_stats):
            # ID
            self.analytics_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            
            # Название
            self.analytics_table.setItem(i, 1, QTableWidgetItem(stat['name']))
            
            # Категория
            self.analytics_table.setItem(i, 2, QTableWidgetItem(stat['category']))
            
            # Количество заказов
            self.analytics_table.setItem(i, 3, QTableWidgetItem(str(stat['count'])))
            
            # Общая сумма
            self.analytics_table.setItem(i, 4, QTableWidgetItem(f"{stat['total']:.2f}"))
            
            # Средняя цена
            avg_price = stat['avg_price'] if stat['count'] > 0 else 0
            self.analytics_table.setItem(i, 5, QTableWidgetItem(f"{avg_price:.2f}"))
            
            # Минимальная цена
            self.analytics_table.setItem(i, 6, QTableWidgetItem(f"{stat['min_price']:.2f}"))
            
            # Максимальная цена
            self.analytics_table.setItem(i, 7, QTableWidgetItem(f"{stat['max_price']:.2f}"))
            
            # Среднее время приготовления
            avg_time = stat['avg_cooking_time'] if stat['count'] > 0 else 0
            self.analytics_table.setItem(i, 8, QTableWidgetItem(f"{avg_time:.1f}"))
        # --- обновим график ---
        self.update_chart(filtered_stats)

    def update_chart(self, stats):
        # Построение графика количества заказов по блюдам
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        names = [stat['name'] for stat in stats]
        counts = [stat['count'] for stat in stats]
        ax.bar(names, counts, color='#4a90e2')
        ax.set_title('Количество заказов по блюдам')
        ax.set_xlabel('Блюдо')
        ax.set_ylabel('Количество заказов')
        ax.tick_params(axis='x', rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()

    def export_to_csv(self):
        # Экспорт данных в CSV файл и графика в PNG
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить как CSV",
                f"analytics_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            if not filename:
                return
            # --- Сохраняем график как PNG ---
            png_filename = filename.rsplit('.', 1)[0] + '.png'
            self.figure.savefig(png_filename, bbox_inches='tight')
            # --- Конец блока PNG ---
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                # Заголовки
                headers = [
                    'ID', 'Название', 'Категория', 'Количество заказов',
                    'Общая сумма', 'Средняя цена', 'Мин. цена', 'Макс. цена',
                    'Ср. время приготовления'
                ]
                f.write(';'.join(headers) + '\n')
                # Данные
                date_pattern = re.compile(r'^(\d{4})-(\d{2})-(\d{2})')
                for row in range(self.analytics_table.rowCount()):
                    row_data = []
                    for col in range(self.analytics_table.columnCount()):
                        item = self.analytics_table.item(row, col)
                        text = item.text() if item else ''
                        # Попытка привести к формату ДД.ММ.ГГГГ если это дата
                        match = date_pattern.match(text)
                        if match:
                            text = f"{match.group(3)}.{match.group(2)}.{match.group(1)}"
                        row_data.append(text)
                    f.write(';'.join(row_data) + '\n')
            QMessageBox.information(self, "Экспорт завершён", f"Данные успешно экспортированы в файл:\n{filename}\nГрафик сохранён как:\n{png_filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Ошибка при экспорте в CSV: {e}")

    def export_to_html(self):
        # Экспорт данных в HTML файл и графика в PNG
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчет",
            "",
            "HTML Files (*.html)"
        )
        
        if filename:
            # --- Сохраняем график как PNG ---
            png_filename = filename.rsplit('.', 1)[0] + '.png'
            self.figure.savefig(png_filename, bbox_inches='tight')
            # --- Конец блока PNG ---
            with open(filename, 'w', encoding='utf-8') as file:
                html = '<html><head><style>'
                html += 'table { border-collapse: collapse; width: 100%; }'
                html += 'th, td { border: 1px solid black; padding: 8px; text-align: left; }'
                html += 'tr:nth-child(even) { background-color: #f2f2f2; }'
                html += '</style></head><body>'
                html += '<h2>Отчет по заказам</h2>'
                # --- Вставляем график ---
                html += f'<img src="{png_filename.split("/")[-1]}" alt="График аналитики" style="max-width:100%;height:auto;"><br><br>'
                # --- Конец блока графика ---
                html += '<table><tr>'
                
                # Заголовки
                headers = ['Блюдо', 'Количество заказов', 'Сумма заказов', 'Средний чек']
                for header in headers:
                    html += f'<th>{header}</th>'
                html += '</tr>'
                
                # Данные
                for row in range(self.analytics_table.rowCount()):
                    html += '<tr>'
                    for col in range(self.analytics_table.columnCount()):
                        item = self.analytics_table.item(row, col)
                        html += f'<td>{item.text() if item else ""}</td>'
                    html += '</tr>'
                
                html += '</table></body></html>'
                file.write(html)
            QMessageBox.information(self, "Экспорт завершён", f"HTML-отчёт сохранён в файл:\n{filename}\nГрафик сохранён как:\n{png_filename}") 