import csv
import random
from datetime import datetime, timedelta

OUTPUT_FILE = "orders_1M.csv"
TOTAL_ROWS = 1_000_000
CHUNK_SIZE = 100_000  # write in batches

# Predefined values
order_statuses = ["PENDING", "SHIPPED", "DELIVERED", "CANCELLED"]
countries = ["India", "USA", "UK", "Germany", "Canada"]
states = ["UP", "MH", "KA", "DL", "TN"]

start_date = datetime(2020, 1, 1)

def generate_row(order_id):
    return [
        order_id,
        random.randint(1000, 9999),  # customer_id
        round(random.uniform(10, 1000), 2),  # amount
        random.choice(order_statuses),
        random.choice(countries),
        random.choice(states),
        (start_date + timedelta(days=random.randint(0, 1500))).strftime("%Y-%m-%d")
    ]

def write_csv():
    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        

        # Header
        writer.writerow([
            "order_id", "customer_id", "amount",
            "order_status", "country", "state", "order_date"
        ])

        for start in range(0, TOTAL_ROWS, CHUNK_SIZE):
            batch = []
            for i in range(start, min(start + CHUNK_SIZE, TOTAL_ROWS)):
                batch.append(generate_row(i + 1))
            
            writer.writerows(batch)
            print(f"Written {start + len(batch)} rows")

if __name__ == "__main__":
    write_csv()