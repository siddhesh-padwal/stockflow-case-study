CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_warehouse_company ON warehouses(company_id);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    price NUMERIC(12,2) NOT NULL,
    product_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    quantity INT NOT NULL DEFAULT 0,
    UNIQUE(product_id, warehouse_id)
);

CREATE TABLE inventory_movements (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    change INT NOT NULL,
    reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255),
    contact_email VARCHAR(255)
);
CREATE TABLE product_suppliers (
    product_id INT REFERENCES products(id),
    supplier_id INT REFERENCES suppliers(id),
    PRIMARY KEY(product_id, supplier_id)
);
CREATE TABLE product_bundles (
    bundle_id INT REFERENCES products(id),
    component_product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    PRIMARY KEY(bundle_id, component_product_id)
);
