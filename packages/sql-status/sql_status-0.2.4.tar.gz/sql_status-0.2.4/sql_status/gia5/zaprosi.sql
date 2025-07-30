CREATE TABLE users (
    user_id INT IDENTITY PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager', 'worker'))
);

CREATE TABLE product_types (
    product_type_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    coefficient FLOAT CHECK (coefficient >= 0)
);

CREATE TABLE products (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(150) NOT NULL,
    article NVARCHAR(50) NOT NULL UNIQUE,
    min_price DECIMAL(10,2) CHECK (min_price >= 0),
    product_type_id INT NOT NULL
);

CREATE TABLE material_types (
    material_type_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    defect_percent FLOAT CHECK (defect_percent >= 0 AND defect_percent <= 100)
);

CREATE TABLE unit_types (
    unit_type_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE materials (
    material_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    material_type_id INT NOT NULL,
    unit_price DECIMAL(10, 2) CHECK (unit_price >= 0),
    stock_qty FLOAT CHECK (stock_qty >= 0),
    min_qty FLOAT CHECK (min_qty >= 0),
    package_qty FLOAT CHECK (package_qty >= 0),
    unit_type_id INT NOT NULL
);

CREATE TABLE product_materials (
    product_material_id INT IDENTITY(1,1) PRIMARY KEY,
    product_id INT NOT NULL,
    material_id INT NOT NULL,
    required_qty FLOAT CHECK (required_qty > 0)
);


ALTER TABLE products
ADD CONSTRAINT fk_products_product_type
FOREIGN KEY (product_type_id) REFERENCES product_types(product_type_id);

ALTER TABLE materials
ADD CONSTRAINT fk_materials_material_type
FOREIGN KEY (material_type_id) REFERENCES material_types(material_type_id);

ALTER TABLE materials
ADD CONSTRAINT fk_materials_unit_type
FOREIGN KEY (unit_type_id) REFERENCES unit_types(unit_type_id);

ALTER TABLE product_materials
ADD CONSTRAINT fk_product_materials_product
FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE product_materials
ADD CONSTRAINT fk_product_materials_material
FOREIGN KEY (material_id) REFERENCES materials(material_id);
