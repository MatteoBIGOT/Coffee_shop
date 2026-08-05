CREATE DATABASE IF NOT EXISTS coffee_shop
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE coffee_shop;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;


-- =========================
-- USERS
-- =========================

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('client', 'seller') NOT NULL DEFAULT 'client',

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB;


-- =========================
-- CATEGORIES
-- =========================

CREATE TABLE categories (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_categories_name (name)
) ENGINE=InnoDB;


-- =========================
-- PRODUCTS
-- =========================

CREATE TABLE products (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image VARCHAR(255),
    category_id INT DEFAULT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (id),

    KEY idx_products_category_id (category_id),
    KEY idx_products_active (active),

    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;


-- =========================
-- ORDERS
-- =========================

CREATE TABLE orders (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    state VARCHAR(50) NOT NULL DEFAULT 'pending',
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    PRIMARY KEY (id),

    KEY idx_orders_user_id (user_id),
    KEY idx_orders_state (state),

    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =========================
-- ORDER ITEMS
-- =========================

CREATE TABLE order_items (
    id INT NOT NULL AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,

    PRIMARY KEY (id),

    KEY idx_order_items_order_id (order_id),
    KEY idx_order_items_product_id (product_id),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =========================
-- CATEGORIES DE BASE
-- =========================

INSERT INTO categories (name)
VALUES
('Cafés'),
('Thés'),
('Pâtisseries');


-- =========================
-- VERIFICATION
-- =========================

SELECT * FROM users;
SELECT * FROM categories;
SELECT * FROM products;
SELECT * FROM orders;
SELECT * FROM order_items;