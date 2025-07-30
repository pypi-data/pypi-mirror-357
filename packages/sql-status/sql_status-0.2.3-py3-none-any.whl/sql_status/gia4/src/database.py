import pyodbc
from contextlib import contextmanager

class Database:
    def __init__(self):
        # Для локального подключения (Trusted_Connection)
        self.connection_string = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=SIN2T;'
            'DATABASE=GIA4;'
            'Trusted_Connection=yes;'
        )
        # Для подключения к реальному серверу с логином/паролем (замените параметры и раскомментируйте строку ниже):
        # self.connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.1.233;DATABASE=demo_wibe;UID=admin;PWD=123456'
    @contextmanager
    def connect(self):
        conn = pyodbc.connect(self.connection_string)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query, params=None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
            
    def execute_non_query(self, query, params=None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()

    def execute_insert_returning(self, query, params=None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            conn.commit()
            return result

    # --- USERS ---
    def get_user_by_credentials(self, username, password):
        query = """
        SELECT user_id, username, role FROM users WHERE username=? AND password_hash=?
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username, password))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'username': row[1], 'role': row[2]}
            return None

    def register_user(self, username, password, role):
        query = """
        INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
        """
        params = (username, password, role)
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def get_users(self):
        return self.execute_query("SELECT user_id, username, role FROM users")

    def delete_user(self, user_id):
        self.delete_by_id("users", "user_id", user_id)

    def update_user_role(self, user_id, role):
        self.update_field_by_id("users", "role", role, "user_id", user_id)

    # --- UNIVERSAL HELPERS ---
    def get_single_value(self, query, params=None):
        row = self.execute_query(query, params)
        return row[0][0] if row else None

    def delete_by_id(self, table, id_field, id_value):
        self.execute_non_query(f"DELETE FROM {table} WHERE {id_field}=?", (id_value,))

    def update_field_by_id(self, table, field, value, id_field, id_value):
        self.execute_non_query(f"UPDATE {table} SET {field}=? WHERE {id_field}=?", (value, id_value))

    # --- PRODUCTS ---
    def get_product_types(self):
        return self.execute_query("SELECT name FROM product_types")

    def get_product_types_with_id(self):
        return self.execute_query("SELECT product_type_id, name FROM product_types")

    def get_products(self, filter_val=None, type_filter=None, sort_index=0):
        query = """
        SELECT p.product_id, p.name, pt.name, p.article, p.min_price, pt.coefficient
        FROM products p
        LEFT JOIN product_types pt ON p.product_type_id = pt.product_type_id
        """
        col_map = [
            "p.product_id", "p.name", "pt.name", "p.article", "p.min_price", "pt.coefficient"
        ]
        params = []
        where_clauses = []
        if filter_val:
            where_clauses.append("(" + " OR ".join([f"{col} LIKE ?" for col in col_map]) + ")")
            params.extend([f"%{filter_val}%"] * len(col_map))
        if type_filter and type_filter != "Все типы" and type_filter != "Ошибка загрузки типов":
            where_clauses.append("pt.name = ?")
            params.append(type_filter)
        where = ""
        if where_clauses:
            where = " WHERE " + " AND ".join(where_clauses)
        # Сортировка
        if sort_index == 1:
            order = " ORDER BY p.min_price ASC, p.product_id DESC"
        elif sort_index == 2:
            order = " ORDER BY p.min_price DESC, p.product_id DESC"
        else:
            order = " ORDER BY p.product_id DESC"
        full_query = query + where + order
        return self.execute_query(full_query, params) if params else self.execute_query(full_query)

    def get_product_by_id(self, product_id):
        row = self.execute_query("""
            SELECT p.name, pt.name, p.article, p.min_price, pt.coefficient, p.product_type_id
            FROM products p LEFT JOIN product_types pt ON p.product_type_id = pt.product_type_id WHERE p.product_id=?
        """, (product_id,))
        return row[0] if row else None

    def update_product(self, product_id, name, product_type_id, article, min_price):
        self.execute_non_query(
            "UPDATE products SET name=?, product_type_id=?, article=?, min_price=? WHERE product_id=?",
            (name, product_type_id, article, min_price, product_id)
        )

    def update_product_type_coefficient(self, product_type_id, coefficient):
        self.update_field_by_id("product_types", "coefficient", coefficient, "product_type_id", product_type_id)

    def get_product_type_id_by_product(self, product_id):
        return self.get_single_value("SELECT product_type_id FROM products WHERE product_id=?", (product_id,))

    def update_product_min_price(self, product_id, min_price):
        self.update_field_by_id("products", "min_price", min_price, "product_id", product_id)

    def delete_product(self, product_id):
        self.delete_by_id("products", "product_id", product_id)

    def add_product(self, name, product_type_id, article, min_price):
        query = """
        INSERT INTO products (name, product_type_id, article, min_price) OUTPUT INSERTED.product_id VALUES (?, ?, ?, ?)
        """
        row = self.execute_insert_returning(query, (name, product_type_id, article, min_price))
        return row[0] if row else None

    # --- MATERIALS ---
    def get_materials(self):
        return self.execute_query("SELECT material_id, name, defect_percent FROM materials")

    def add_material(self, name, defect_percent):
        query = "INSERT INTO materials (name, defect_percent) OUTPUT INSERTED.material_id VALUES (?, ?)"
        row = self.execute_insert_returning(query, (name, defect_percent))
        return row[0] if row else None

    # --- WORKSHOPS ---
    def get_workshops(self):
        return self.execute_query("SELECT workshop_id, name, type, staff_count FROM workshops")

    def add_workshop(self, name, type, staff_count):
        query = "INSERT INTO workshops (name, type, staff_count) OUTPUT INSERTED.workshop_id VALUES (?, ?, ?)"
        row = self.execute_insert_returning(query, (name, type, staff_count))
        return row[0] if row else None

    # --- PRODUCT WORKSHOPS ---
    def get_product_workshops(self, product_id):
        query = """
        SELECT pw.product_workshop_id, w.name, pw.production_time_hours
        FROM product_workshops pw
        LEFT JOIN workshops w ON pw.workshop_id = w.workshop_id
        WHERE pw.product_id = ?
        """
        return self.execute_query(query, (product_id,))

    def add_product_workshop(self, product_id, workshop_id, production_time_hours):
        # Получаем имя продукта и цеха для совместимости со старой структурой
        product_name = self.get_single_value("SELECT name FROM products WHERE product_id=?", (product_id,))
        workshop_name = self.get_single_value("SELECT name FROM workshops WHERE workshop_id=?", (workshop_id,))
        query = "INSERT INTO product_workshops (product_id, workshop_id, production_time_hours, product_name, workshop_name) OUTPUT INSERTED.product_workshop_id VALUES (?, ?, ?, ?, ?)"
        row = self.execute_insert_returning(query, (product_id, workshop_id, production_time_hours, product_name, workshop_name))
        return row[0] if row else None

    def calculate_total_production_time(self, product_id):
        query = "SELECT SUM(production_time_hours) FROM product_workshops WHERE product_id = ?"
        return self.get_single_value(query, (product_id,))

# --- DB PING ---
def ping_db():
    try:
        db = Database()
        conn = pyodbc.connect(db.connection_string, timeout=3)
        print("Успешное подключение к базе данных!")
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False
