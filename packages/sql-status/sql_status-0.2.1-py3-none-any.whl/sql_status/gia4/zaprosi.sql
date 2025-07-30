-- Таблица: Пользователи
CREATE TABLE users (
    user_id INT IDENTITY PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager', 'worker'))
);


-- Таблица: Типы продукции
CREATE TABLE product_types (
    product_type_id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(100) UNIQUE NOT NULL,
    coefficient FLOAT CHECK (coefficient >= 0)
);

-- Таблица: Материалы
CREATE TABLE materials (
    material_id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(100) UNIQUE NOT NULL,
    defect_percent FLOAT CHECK (defect_percent >= 0 AND defect_percent <= 100)
);

-- Таблица: Цеха
CREATE TABLE workshops (
    workshop_id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(150) UNIQUE NOT NULL,
    type NVARCHAR(50),
    staff_count INT CHECK (staff_count > 0)
);

-- Таблица: Продукция
CREATE TABLE products (
    product_id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(150) NOT NULL,
    article NVARCHAR(50) UNIQUE NOT NULL,
    min_price DECIMAL(10,2) CHECK (min_price >= 0),
    product_type NVARCHAR(100) NOT NULL,  -- временно по имени, заменим на ID после
    material NVARCHAR(100) NOT NULL       -- временно по имени, заменим на ID после
);

-- Таблица: Продукция и цеха
CREATE TABLE product_workshops (
    product_workshop_id INT IDENTITY PRIMARY KEY,
    product_name NVARCHAR(150) NOT NULL,     -- временно по имени, позже заменим на ID
    workshop_name NVARCHAR(150) NOT NULL,    -- временно по имени, позже заменим на ID
    production_time_hours FLOAT CHECK (production_time_hours > 0)
);


-- Добавим поля с ID в таблицу products и product_workshops, если ещё не созданы
ALTER TABLE products ADD product_type_id INT, material_id INT;
ALTER TABLE product_workshops ADD product_id INT, workshop_id INT;

-- Затем создаем связи (когда ID уже занесены)
ALTER TABLE products
    ADD CONSTRAINT fk_products_type FOREIGN KEY (product_type_id)
    REFERENCES product_types(product_type_id);

ALTER TABLE products
    ADD CONSTRAINT fk_products_material FOREIGN KEY (material_id)
    REFERENCES materials(material_id);

ALTER TABLE product_workshops
    ADD CONSTRAINT fk_product_workshop_product FOREIGN KEY (product_id)
    REFERENCES products(product_id);

ALTER TABLE product_workshops
    ADD CONSTRAINT fk_product_workshop_workshop FOREIGN KEY (workshop_id)
    REFERENCES workshops(workshop_id);