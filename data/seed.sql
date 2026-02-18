-- Customers Table
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    account_status TEXT,
    created_at TEXT
);

-- Tickets Table
DROP TABLE IF EXISTS tickets;
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    subject TEXT,
    description TEXT,
    status TEXT,
    priority TEXT,
    created_at TEXT,
    resolved_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Interactions Table
DROP TABLE IF EXISTS interactions;
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER,
    agent_name TEXT,
    message TEXT,
    created_at TEXT,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);

-- Insert Customers
INSERT INTO customers (name, email, phone, account_status, created_at) VALUES
('Ema Patel', 'ema.patel@email.com', '123-456-7890', 'Active', '2023-01-10'),
('John Miller', 'john.m@email.com', '111-222-3333', 'Active', '2022-11-20'),
('Sophia Lee', 'sophia.l@email.com', '999-888-7777', 'Suspended', '2023-03-05'),
('Liam Brown', 'liam.b@email.com', '555-666-7777', 'Active', '2023-06-15'),
('Olivia Smith', 'olivia.s@email.com', '444-555-6666', 'Active', '2023-07-21');

-- Insert Tickets
INSERT INTO tickets (customer_id, subject, description, status, priority, created_at, resolved_at) VALUES
(1, 'Refund not received', 'Customer claims refund not processed after 30 days.', 'Open', 'High', '2024-01-05', NULL),
(1, 'Late delivery', 'Package delivered 5 days late.', 'Closed', 'Medium', '2023-12-01', '2023-12-05'),
(2, 'Damaged item', 'Received damaged product.', 'Closed', 'High', '2023-11-10', '2023-11-12'),
(3, 'Account locked', 'Cannot access account.', 'Open', 'High', '2024-01-15', NULL),
(4, 'Change shipping address', 'Request to update shipping address.', 'Closed', 'Low', '2023-09-20', '2023-09-21'),
(5, 'Refund inquiry', 'Asking about refund eligibility after 40 days.', 'Open', 'Medium', '2024-02-01', NULL);

-- Insert Interactions
INSERT INTO interactions (ticket_id, agent_name, message, created_at) VALUES
(1, 'Agent Sarah', 'Requested transaction details from customer.', '2024-01-06'),
(1, 'Agent Sarah', 'Waiting for confirmation from finance team.', '2024-01-08'),
(4, 'Agent Mark', 'Provided password reset instructions.', '2024-01-16');
