CREATE TABLE Customer (
    customer_id INT,
    name VARCHAR(255),
    email VARCHAR(255),
    PRIMARY KEY (customer_id)
);

CREATE TABLE Product (
    product_id INT,
    name VARCHAR(255),
    price DECIMAL(10,2),
    PRIMARY KEY (product_id)
);

CREATE TABLE Order (
    order_id INT,
    order_date DATE,
    total DECIMAL(10,2),
    PRIMARY KEY (order_id)
);

CREATE TABLE Contains (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES Order(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);