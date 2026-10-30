# ============================================================
# stocks.py - STOCKS MANAGEMENT SYSTEM (run: python stocks.py)
# ------------------------------------------------------------
# Contains the CRUD operations and the menu loop.
# Connection + the run_sql() query runner live in database.py.
#
# VALIDATION STYLE: every input is checked once. If the value is
# not valid, an [ERROR] is printed and the user goes back to the
# menu instead of being asked again.
# ============================================================
# clint
from mysql.connector import Error
from database import open_database, run_sql, close_database

MENU_TEXT = """
========================================
      STOCKS MANAGEMENT SYSTEM
========================================
 1. Add Stock    (Create)
 2. View Stocks  (Read)
 3. Update Stock (Update)
 4. Delete Stock (Delete)
 5. Exit
----------------------------------------"""


# ------------------------------------------------------------
# CREATE - Add a new stock record
# ------------------------------------------------------------
def create_stock(conn):
    print("\n--- ADD A NEW STOCK ---")

    # Validation: item name (checked once, cancels if blank)
    item_name = input("Enter item name: ").strip()
    if item_name == "":
        print("[ERROR] Item name cannot be empty. Returning to menu.")
        return

    # Validation: quantity (whole number, 0 or higher)
    quantity_raw = input("Enter quantity on hand: ").strip()
    try:
        quantity = int(quantity_raw)
        if quantity < 0:
            print("[ERROR] Quantity cannot be negative. Returning to menu.")
            return
    except ValueError:
        print("[ERROR] Quantity must be a whole number (e.g. 20). Returning to menu.")
        return

    # Validation: price (positive decimal)
    price_raw = input("Enter price per unit: ").strip()
    try:
        price = float(price_raw)
        if price <= 0:
            print("[ERROR] Price must be a positive number. Returning to menu.")
            return
    except ValueError:
        print("[ERROR] Price must be a number (e.g. 25.00). Returning to menu.")
        return

    try:
        # Parameterized query (%s) - prevents SQL injection
        _, new_id, _ = run_sql(
            conn,
            "INSERT INTO stocks (item_name, quantity, price, status) VALUES (%s, %s, %s, %s)",
            (item_name, quantity, price, "Available"),
        )
        print(f"[SUCCESS] Stock added for '{item_name}' with ID {new_id}.")
    except Error as err:
        print(f"[ERROR] Database error while adding stock: {err}")


# ------------------------------------------------------------
# READ - Display all stock records
# ------------------------------------------------------------
def read_stocks(conn):
    try:
        rows, _, _ = run_sql(conn, "SELECT * FROM stocks", fetch=True)
        if not rows:
            print("\n[INFO] No stocks found in the database.")
            return

        print("\n" + "=" * 62)
        print(f"{'ID':<6}{'ITEM NAME':<25}{'QTY':>6}{'PRICE':>10}  {'STATUS':<13}")
        print("-" * 62)
        for rec in rows:  # rows are dictionaries because the cursor is dictionary=True
            print(f"{rec['stock_id']:<6}{rec['item_name']:<25}"
                  f"{rec['quantity']:>6}{float(rec['price']):>10.2f}  {rec['status']:<13}")
        print("=" * 62)
        print(f"[SUCCESS] {len(rows)} record(s) displayed.")
    except Error as err:
        print(f"[ERROR] Database error while fetching stocks: {err}")


# ------------------------------------------------------------
# UPDATE - Change the quantity of an existing stock
#     Quantity 0 automatically sets the status to 'Sold Out'.
# ------------------------------------------------------------
def adjust_quantity(conn):
    print("\n--- UPDATE STOCK QUANTITY ---")

    # Validation: stock ID (checked once, cancels if invalid)
    stock_id_raw = input("Enter the Stock ID to update: ").strip()
    try:
        stock_id = int(stock_id_raw)
        if stock_id < 1:
            print("[ERROR] ID must be 1 or higher. Returning to menu.")
            return
    except ValueError:
        print("[ERROR] ID must be a whole number (e.g. 3). Returning to menu.")
        return

    try:
        # Step 1: verify the record exists (parameterized query)
        rows, _, _ = run_sql(
            conn,
            "SELECT stock_id, item_name, quantity FROM stocks WHERE stock_id = %s",
            (stock_id,),
            fetch=True,
        )
        if not rows:
            print(f"[ERROR] No stock found with ID {stock_id}. Returning to menu.")
            return
        rec = rows[0]
        print(f"Found stock: #{rec['stock_id']} | {rec['item_name']} | "
              f"current quantity: {rec['quantity']}")

        # Step 2: ask for the new quantity (0 is allowed)
        quantity_raw = input("Enter the new quantity (0 to mark as Sold Out): ").strip()
        try:
            new_quantity = int(quantity_raw)
            if new_quantity < 0:
                print("[ERROR] Quantity cannot be negative. Returning to menu.")
                return
        except ValueError:
            print("[ERROR] Quantity must be a whole number (e.g. 20). Returning to menu.")
            return

        # Step 3: update the record (parameterized query)
        new_status = "Sold Out" if new_quantity == 0 else "Available"
        _, _, affected = run_sql(
            conn,
            "UPDATE stocks SET quantity = %s, status = %s WHERE stock_id = %s",
            (new_quantity, new_status, stock_id),
        )
        print(f"[SUCCESS] Stock #{stock_id} '{rec['item_name']}' updated: quantity "
              f"{new_quantity} ({new_status}). [{affected} row(s) affected]")
    except Error as err:
        print(f"[ERROR] Database error while updating stock: {err}")


# ------------------------------------------------------------
# DELETE - Remove a stock record (with y/n confirmation)
# ------------------------------------------------------------
def remove_stock(conn):
    print("\n--- DELETE A STOCK ---")

    # Validation: stock ID (checked once, cancels if invalid)
    stock_id_raw = input("Enter the Stock ID to delete: ").strip()
    try:
        stock_id = int(stock_id_raw)
        if stock_id < 1:
            print("[ERROR] ID must be 1 or higher. Returning to menu.")
            return
    except ValueError:
        print("[ERROR] ID must be a whole number (e.g. 3). Returning to menu.")
        return

    try:
        # Step 1: verify the record exists (parameterized query)
        rows, _, _ = run_sql(
            conn,
            "SELECT stock_id, item_name, quantity, price FROM stocks WHERE stock_id = %s",
            (stock_id,),
            fetch=True,
        )
        if not rows:
            print(f"[ERROR] No stock found with ID {stock_id}. Returning to menu.")
            return
        rec = rows[0]
        print(f"Found stock: #{rec['stock_id']} | {rec['item_name']} | "
              f"qty: {rec['quantity']} | {float(rec['price']):.2f}")

        # Step 2: confirmation
        answer = input("Are you sure you want to DELETE this record? (y/n): ").strip().lower()
        if answer != "y":
            print("[INFO] Delete operation cancelled by user.")
            return

        # Step 3: delete the record (parameterized query)
        _, _, affected = run_sql(conn, "DELETE FROM stocks WHERE stock_id = %s", (stock_id,))
        print(f"[SUCCESS] Stock #{stock_id} '{rec['item_name']}' has been deleted. "
              f"[{affected} row(s) affected]")
    except Error as err:
        print(f"[ERROR] Database error while deleting stock: {err}")


# ------------------------------------------------------------
# MENU LOOP
# ------------------------------------------------------------
def run():
    conn = open_database()
    if conn is None:
        print("[ERROR] Cannot start the application without a database connection.")
        return

    try:
        while True:
            print(MENU_TEXT)
            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                create_stock(conn)
            elif choice == "2":
                read_stocks(conn)
            elif choice == "3":
                adjust_quantity(conn)
            elif choice == "4":
                remove_stock(conn)
            elif choice == "5":
                print("[INFO] Closing the database connection...")
                close_database(conn)
                break
            else:
                print("[ERROR] Unknown option. Please enter 1, 2, 3, 4 or 5.")
    except KeyboardInterrupt:
        print("\n[INFO] Program interrupted. Closing connection...")
        close_database(conn)


if __name__ == "__main__":
    run()
