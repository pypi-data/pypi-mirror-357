import pyodbc
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=SIN2T;'
        'DATABASE=GIA;'
        'Trusted_Connection=yes;'
    )


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

    def get_user_by_credentials(self, username, password):
        query = """
        SELECT user_id, username, role, partner_id FROM users WHERE username=? AND password_hash=?
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username, password))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'username': row[1], 'role': row[2], 'partner_id': row[3]}
            return None

    def register_user(self, username, password, role, partner_id=None):
        if partner_id is not None:
            query = """
            INSERT INTO users (username, password_hash, role, partner_id) VALUES (?, ?, ?, ?)
            """
            params = (username, password, role, partner_id)
        else:
            query = """
            INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
            """
            params = (username, password, role)
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    # --- UNIVERSAL HELPERS ---
    def get_single_value(self, query, params=None):
        row = self.execute_query(query, params)
        return row[0][0] if row else None

    def delete_by_id(self, table, id_field, id_value):
        self.execute_non_query(f"DELETE FROM {table} WHERE {id_field}=?", (id_value,))

    def update_field_by_id(self, table, field, value, id_field, id_value):
        self.execute_non_query(f"UPDATE {table} SET {field}=? WHERE {id_field}=?", (value, id_value))

    # --- PARTNERS METHODS ---
    def get_partner_types(self):
        query = "SELECT name FROM partner_types"
        return self.execute_query(query)

    def get_partner_type_id(self, type_name):
        return self.get_single_value("SELECT partner_type_id FROM partner_types WHERE name=?", (type_name,))

    def get_partners(self, filter_val=None, type_filter=None, rating_filter=None, sort_index=0):
        query = """
        SELECT p.partner_id, pt.name, p.name, p.director_name, p.email, p.phone, p.legal_address, p.inn, p.rating
        FROM partners p
        LEFT JOIN partner_types pt ON p.partner_type_id = pt.partner_type_id
        """
        col_map = [
            "p.partner_id", "pt.name", "p.name", "p.director_name", "p.email",
            "p.phone", "p.legal_address", "p.inn", "p.rating"
        ]
        params = []
        where_clauses = []
        if filter_val:
            where_clauses.append("(" + " OR ".join([f"{col} LIKE ?" for col in col_map]) + ")")
            params.extend([f"%{filter_val}%"] * len(col_map))
        if type_filter and type_filter != "Все типы" and type_filter != "Ошибка загрузки типов":
            where_clauses.append("pt.name = ?")
            params.append(type_filter)
        if rating_filter == "0-5":
            where_clauses.append("p.rating >= 0 AND p.rating < 5")
        elif rating_filter == "5-8":
            where_clauses.append("p.rating >= 5 AND p.rating < 8")
        elif rating_filter == "8-10":
            where_clauses.append("p.rating >= 8 AND p.rating <= 10")
        where = ""
        if where_clauses:
            where = " WHERE " + " AND ".join(where_clauses)
        if sort_index == 0:
            order = " ORDER BY p.partner_id DESC"
        elif sort_index == 1:
            order = " ORDER BY p.rating DESC, p.partner_id DESC"
        else:
            order = " ORDER BY p.rating ASC, p.partner_id DESC"
        full_query = query + where + order
        return self.execute_query(full_query, params) if params else self.execute_query(full_query)

    def update_partner_rating(self, partner_id, value):
        self.update_field_by_id("partners", "rating", value, "partner_id", partner_id)

    def get_partner_by_id(self, partner_id):
        query = """
            SELECT pt.name, p.name, p.director_name, p.email, p.phone, p.legal_address, p.inn
            FROM partners p LEFT JOIN partner_types pt ON p.partner_type_id = pt.partner_type_id WHERE p.partner_id=?
        """
        return self.execute_query(query, (partner_id,))

    def add_partner_type(self, type_name):
        # Для MSSQL OUTPUT INSERTED.partner_type_id, для SQLite можно RETURNING partner_type_id
        row = self.execute_insert_returning(
            "INSERT INTO partner_types (name) OUTPUT INSERTED.partner_type_id VALUES (?)", (type_name,))
        return row[0] if row else None

    def update_partner(self, partner_id, type_id, name, director, email, phone, address, inn):
        self.execute_non_query(
            "UPDATE partners SET partner_type_id=?, name=?, director_name=?, email=?, phone=?, legal_address=?, inn=? WHERE partner_id=?",
            (type_id, name, director, email, phone, address, inn, partner_id)
        )

    def delete_partner(self, partner_id):
        self.delete_by_id("partners", "partner_id", partner_id)

    # --- PRODUCTS METHODS ---
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

def ping_db():
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=SIN2T;'
        'DATABASE=GIA;'
        'Trusted_Connection=yes;'
    )

    try:
        conn = pyodbc.connect(conn_str, timeout=3)
        print("Успешное подключение к базе данных!")
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False
