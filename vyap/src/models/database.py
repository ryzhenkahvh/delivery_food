import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="food_delivery.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_tables()

    def create_tables(self):
        # Создание и обновление структуры таблиц в базе данных
        cursor = self.conn.cursor()
        
        # Получение текущей схемы таблицы customers
        cursor.execute("PRAGMA table_info(customers)")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        # Обновление таблицы customers если нужно
        if 'full_name' in columns and 'name' not in columns:
            cursor.execute('ALTER TABLE customers RENAME COLUMN full_name TO name')
        
        if 'email' not in columns:
            cursor.execute('ALTER TABLE customers ADD COLUMN email TEXT')
        
        # Обновление таблицы orders если нужно
        cursor.execute("PRAGMA table_info(orders)")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        if 'courier' in columns:
            # Создаем временную таблицу с новой структурой
            cursor.execute('''
                CREATE TABLE orders_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    dish_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (dish_id) REFERENCES dishes (id)
                )
            ''')
            
            # Копируем данные
            cursor.execute('''
                INSERT INTO orders_new (id, customer_id, dish_id, status, date)
                SELECT id, customer_id, dish_id, status, order_datetime
                FROM orders
            ''')
            
            # Удаляем старую таблицу и переименовываем новую
            cursor.execute('DROP TABLE orders')
            cursor.execute('ALTER TABLE orders_new RENAME TO orders')
        
        # Создание индексов для оптимизации запросов
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_dish ON orders(dish_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(date)')
        
        self.conn.commit()

    def get_order_statistics(self, date_from=None):
        # Получение статистики по заказам
        cursor = self.conn.cursor()
        
        # Базовый запрос для получения статистики
        query = '''
            SELECT 
                d.name,
                d.category,
                COUNT(o.id) as order_count,
                SUM(d.price) as total_sum,
                AVG(d.price) as avg_price,
                MIN(d.price) as min_price,
                MAX(d.price) as max_price,
                AVG(d.cooking_time) as avg_cooking_time
            FROM dishes d
            LEFT JOIN orders o ON d.id = o.dish_id
        '''
        
        # Добавление фильтра по дате, если указана
        if date_from:
            query += ' WHERE datetime(o.date) >= ?'
            query += ' GROUP BY d.id, d.name, d.category'
            cursor.execute(query, (date_from.strftime('%Y-%m-%d %H:%M:%S'),))
        else:
            query += ' GROUP BY d.id, d.name, d.category'
            cursor.execute(query)
        
        # Формирование результата
        stats = {}
        for row in cursor.fetchall():
            name, category, count, total, avg, min_price, max_price, avg_time = row
            if count is None:  # Если нет заказов для блюда
                count = 0
                total = 0
                avg = 0
                avg_time = 0
            
            stats[name] = {
                'name': name,
                'category': category,
                'count': count,
                'total': total or 0,
                'avg_price': avg or 0,
                'min_price': min_price or 0,
                'max_price': max_price or 0,
                'avg_cooking_time': avg_time or 0
            }
        
        return stats

    # Dish operations
    def add_dish(self, name, category, price, cooking_time):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO dishes (name, category, price, cooking_time)
        VALUES (?, ?, ?, ?)
        ''', (name, category, price, cooking_time))
        self.conn.commit()

    def get_all_dishes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM dishes')
        dishes = cursor.fetchall()
        return dishes

    def update_dish(self, dish_id, name, category, price, cooking_time):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE dishes
        SET name = ?, category = ?, price = ?, cooking_time = ?
        WHERE id = ?
        ''', (name, category, price, cooking_time, dish_id))
        self.conn.commit()

    def delete_dish(self, dish_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM dishes WHERE id = ?', (dish_id,))
        self.conn.commit()

    # Customer operations
    def add_customer(self, name, address, phone, email):
        # Добавление нового клиента с проверкой на дубликаты по имени и телефону или email
        cursor = self.conn.cursor()
        # Проверка на дубликаты по имени и телефону или email
        cursor.execute(
            'SELECT id FROM customers WHERE (name = ? AND phone = ?) OR (email != "" AND email = ?)',
            (name, phone, email)
        )
        if cursor.fetchone():
            raise Exception('Клиент с таким именем и телефоном или email уже существует!')
        cursor.execute(
            'INSERT INTO customers (name, address, phone, email) VALUES (?, ?, ?, ?)',
            (name, address, phone, email)
        )
        self.conn.commit()

    def get_all_customers(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM customers')
        customers = cursor.fetchall()
        return customers

    def update_customer(self, customer_id, name, address, phone, email):
        # Обновление информации о клиенте
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE customers SET name=?, address=?, phone=?, email=? WHERE id=?',
            (name, address, phone, email, customer_id)
        )
        self.conn.commit()

    def delete_customer(self, customer_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        self.conn.commit()

    # Order operations
    def add_order(self, customer_id, dish_id, status):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO orders (customer_id, dish_id, status)
        VALUES (?, ?, ?)
        ''', (customer_id, dish_id, status))
        self.conn.commit()

    def get_all_orders(self):
        # Получение списка всех заказов с информацией о клиентах и блюдах
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                o.id,
                c.name as customer_name,
                d.name as dish_name,
                o.status,
                datetime(o.date) as date,
                c.address,
                c.phone,
                d.category,
                d.price,
                d.cooking_time
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN dishes d ON o.dish_id = d.id
            ORDER BY o.date DESC
        ''')
        return cursor.fetchall()

    def update_order(self, order_id, customer_id, dish_id, status):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE orders
        SET customer_id = ?, dish_id = ?, status = ?
        WHERE id = ?
        ''', (customer_id, dish_id, status, order_id))
        self.conn.commit()

    def delete_order(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        self.conn.commit()

    def get_popular_dishes(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT d.name, COUNT(o.id) as order_count
        FROM dishes d
        LEFT JOIN orders o ON d.id = o.dish_id
        GROUP BY d.id
        ORDER BY order_count DESC
        LIMIT 5
        ''')
        popular_dishes = cursor.fetchall()
        return popular_dishes

    def __del__(self):
        self.conn.close() 