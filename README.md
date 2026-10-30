# Stocks Management System

A console-based (terminal) CRUD application for tracking stocks/items, built with **Python** and **MySQL**. No GUI — everything runs in the terminal with a menu-driven interface.

## Project Files

| File | Purpose |
|------|---------|
| `stocks_db.sql` | SQL script that creates the database `stocks_db` and the table `stocks` |
| `database.py` | Connection setup (`DB_CONFIG`, `open_database`) + one central query runner `run_sql()` that handles parameterized execution, commit/rollback and cursor closing |
| `stocks.py` | CRUD operations + menu loop (run this file to start) |

## Requirements

- Python 3.x
- MySQL Server
- The Python MySQL driver:

```
pip install mysql-connector-python
```

## Setup

1. **Create the database and table** by running the SQL script once. From a terminal, inside this folder:

   ```
   mysql -u root -p < stocks_db.sql
   ```

   (Or open the MySQL monitor, log in, and paste the contents of `stocks_db.sql`.)

2. **Set your MySQL password** — open `database.py` and change this line in `DB_CONFIG`:

   ```python
   "password": "",          # <--- CHANGE THIS to your MySQL password
   ```

3. **Run the application**:

   ```
   python stocks.py
   ```

## Usage

When the app starts, you will see this menu:

```
========================================
      STOCKS MANAGEMENT SYSTEM
========================================
 1. Add Stock    (Create)
 2. View Stocks  (Read)
 3. Update Stock (Update)
 4. Delete Stock (Delete)
 5. Exit
----------------------------------------
```

| Option | What it does |
|--------|--------------|
| 1 | Asks for an item name, quantity and price, then saves a new record with status `Available` |
| 2 | Displays all records in a formatted table (ID, ITEM NAME, QTY, PRICE, STATUS) |
| 3 | Asks for a Stock ID, verifies it exists, then updates the quantity — quantity `0` automatically sets the status to `Sold Out` |
| 4 | Asks for a Stock ID, verifies it exists, asks for a `y/n` confirmation, then deletes the record |
| 5 | Closes the database connection properly and terminates the program |

**How input checking works:** every input is validated once. If the value is invalid (blank name, non-numeric quantity, etc.) an `[ERROR]` message is printed and the user is returned to the menu.

## Database Table Structure

Table name: `stocks` (in database `stocks_db`)

| Column | Type | Notes |
|--------|------|-------|
| `stock_id` | INT | Primary Key, Auto Increment |
| `item_name` | VARCHAR(100) | Not empty |
| `quantity` | INT | Whole number, 0 or more |
| `price` | DECIMAL(10,2) | Positive number |
| `status` | VARCHAR(20) | Defaults to `'Available'`; changes to `'Sold Out'` when quantity is 0 |

## Key Design Points

- **Parameterized SQL ( `%s` )** is used for ALL database operations — no string concatenation — to prevent SQL injection.
- **Central query runner**: every statement passes through the single `run_sql()` helper in `database.py`, which commits writes, rolls back on failure, and closes the cursor in a `finally:` block — cleanup is written once, not per function.
- **Dictionary rows**: the cursor is created with `dictionary=True`, so Read results are printed using row keys like `rec['item_name']`.
- **Input validation**: names cannot be blank; quantity must be a whole number (0+); price must be a positive number parsed with `try...except ValueError`; invalid input cancels back to the menu.
- **Record verification**: Update and Delete check the ID exists before acting; Delete additionally requires a `y/n` confirmation.
- **Exception handling**: every database call runs inside `try...except mysql.connector.Error` (the runner re-raises after rolling back so the caller can print its own `[ERROR]` message).
- **Debugging output**: results are tagged with `[SUCCESS]`, `[ERROR]`, or `[INFO]` so problems are easy to trace and demonstrate during debugging.
