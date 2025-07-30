import pyodbc
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.connection_string = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=SIN2T;'
            'DATABASE=GIA5;'
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
        self.execute_non_query("DELETE FROM users WHERE user_id=?", (user_id,))

    def update_user_role(self, user_id, role):
        self.execute_non_query("UPDATE users SET role=? WHERE user_id=?", (role, user_id))

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
        self.execute_non_query("UPDATE product_types SET coefficient=? WHERE product_type_id=?", (coefficient, product_type_id))

    def get_product_type_id_by_product(self, product_id):
        row = self.execute_query("SELECT product_type_id FROM products WHERE product_id=?", (product_id,))
        return row[0][0] if row else None

    def update_product_min_price(self, product_id, min_price):
        self.execute_non_query("UPDATE products SET min_price=? WHERE product_id=?", (min_price, product_id))

    def delete_product(self, product_id):
        self.execute_non_query("DELETE FROM products WHERE product_id=?", (product_id,))

    def add_product(self, name, product_type_id, article, min_price):
        query = """
        INSERT INTO products (name, product_type_id, article, min_price) OUTPUT INSERTED.product_id VALUES (?, ?, ?, ?)
        """
        row = self.execute_insert_returning(query, (name, product_type_id, article, min_price))
        return row[0] if row else None

    # --- MATERIALS ---
    def get_materials(self):
        return self.execute_query("SELECT material_id, name FROM materials")

    def add_material(self, name, defect_percent):
        query = "INSERT INTO materials (name, defect_percent) OUTPUT INSERTED.material_id VALUES (?, ?)"
        row = self.execute_insert_returning(query, (name, defect_percent))
        return row[0] if row else None

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
