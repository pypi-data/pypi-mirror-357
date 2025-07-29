-- Таблица: Тип продукции
CREATE TABLE product_types (
    product_type_id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(100) UNIQUE,
    coefficient FLOAT CHECK (coefficient >= 0)
);

-- Таблица: Продукция
CREATE TABLE products (
    product_id INT IDENTITY PRIMARY KEY,
    product_type_id INT,
    name NVARCHAR(150),
    article NVARCHAR(50) UNIQUE,
    min_price DECIMAL(10,2) CHECK (min_price >= 0)
);

-- Таблица: Типы партнёров
CREATE TABLE partner_types (
    partner_type_id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(50) UNIQUE
);

-- Таблица: Партнёры
CREATE TABLE partners (
    partner_id INT IDENTITY PRIMARY KEY,
    partner_type_id INT,
    name NVARCHAR(150),
    director_name NVARCHAR(100),
    email NVARCHAR(100),
    phone NVARCHAR(50),
    legal_address NVARCHAR(200),
    inn NVARCHAR(20),
    rating INT CHECK (rating >= 0)
);

-- Таблица: Пользователи
CREATE TABLE users (
    user_id INT IDENTITY PRIMARY KEY,
    username NVARCHAR(50) UNIQUE,
    password_hash NVARCHAR(255),
    role NVARCHAR(50) CHECK (role IN ('admin', 'manager', 'partner')),
    partner_id INT
);

-- Таблица: Заявки
CREATE TABLE applications (
    application_id INT IDENTITY PRIMARY KEY,
    partner_id INT,
    product_id INT,
    quantity INT CHECK (quantity > 0),
    status NVARCHAR(50) CHECK (status IN ('новая', 'выполнено', 'отклонено')) DEFAULT 'новая'
);

-- Таблица: Материалы
CREATE TABLE materials (
    material_type_id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(100) UNIQUE,
    defect_percent FLOAT CHECK (defect_percent >= 0 AND defect_percent <= 100)
);


-- products → product_types
ALTER TABLE products ADD CONSTRAINT fk_products_type
    FOREIGN KEY (product_type_id) REFERENCES product_types(product_type_id);

-- partners → partner_types
ALTER TABLE partners ADD CONSTRAINT fk_partners_type
    FOREIGN KEY (partner_type_id) REFERENCES partner_types(partner_type_id);

-- users → partners
ALTER TABLE users ADD CONSTRAINT fk_users_partner
    FOREIGN KEY (partner_id) REFERENCES partners(partner_id);

-- applications → partners
ALTER TABLE applications ADD CONSTRAINT fk_applications_partner
    FOREIGN KEY (partner_id) REFERENCES partners(partner_id);

-- applications → products
ALTER TABLE applications ADD CONSTRAINT fk_applications_product
    FOREIGN KEY (product_id) REFERENCES products(product_id);

-- orders → applications
ALTER TABLE orders ADD CONSTRAINT fk_orders_application
    FOREIGN KEY (application_id) REFERENCES applications(application_id);
