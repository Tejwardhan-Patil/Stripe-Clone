import psycopg2
import pandas as pd
from datetime import datetime
from decimal import Decimal

# Database configuration
DATABASE = {
    'dbname': 'database',
    'user': 'user',
    'password': 'password',
    'host': 'localhost',
    'port': '5432'
}

# Connect to the database
def db_connect():
    try:
        connection = psycopg2.connect(
            dbname=DATABASE['dbname'],
            user=DATABASE['user'],
            password=DATABASE['password'],
            host=DATABASE['host'],
            port=DATABASE['port']
        )
        return connection
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return None

# Fetch revenue data from the database
def fetch_revenue_data(connection, start_date, end_date):
    query = """
    SELECT
        t.id AS transaction_id,
        t.amount,
        t.currency,
        t.created_at,
        p.name AS product_name,
        u.email AS user_email
    FROM transactions t
    JOIN products p ON t.product_id = p.id
    JOIN users u ON t.user_id = u.id
    WHERE t.created_at BETWEEN %s AND %s AND t.status = 'completed';
    """
    cursor = connection.cursor()
    cursor.execute(query, (start_date, end_date))
    transactions = cursor.fetchall()
    cursor.close()
    return transactions

# Generate a Pandas DataFrame from the fetched revenue data
def create_revenue_dataframe(transactions):
    columns = ['Transaction ID', 'Amount', 'Currency', 'Date', 'Product Name', 'User Email']
    df = pd.DataFrame(transactions, columns=columns)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Amount'] = df['Amount'].apply(Decimal)
    return df

# Calculate total revenue
def calculate_total_revenue(df):
    total_revenue = df['Amount'].sum()
    return total_revenue

# Group revenue by product or service
def revenue_by_product(df):
    revenue_product = df.groupby('Product Name')['Amount'].sum()
    return revenue_product

# Generate monthly revenue breakdown
def monthly_revenue_breakdown(df):
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_revenue = df.groupby('Month')['Amount'].sum()
    return monthly_revenue

# Export report to CSV
def export_to_csv(df, file_name):
    try:
        df.to_csv(file_name, index=False)
        print(f"Report successfully exported to {file_name}")
    except Exception as e:
        print(f"Failed to export report: {str(e)}")

# Generate revenue report
def generate_revenue_report(start_date, end_date):
    connection = db_connect()
    if connection:
        print(f"Generating revenue report from {start_date} to {end_date}")
        transactions = fetch_revenue_data(connection, start_date, end_date)
        if transactions:
            df = create_revenue_dataframe(transactions)

            # Total revenue
            total_revenue = calculate_total_revenue(df)
            print(f"Total Revenue: {total_revenue}")

            # Revenue by product
            revenue_product = revenue_by_product(df)
            print("\nRevenue by Product:")
            for product, revenue in revenue_product.items():
                print(f"{product}: {revenue}")

            # Monthly revenue breakdown
            monthly_revenue = monthly_revenue_breakdown(df)
            print("\nMonthly Revenue Breakdown:")
            for month, revenue in monthly_revenue.items():
                print(f"{month}: {revenue}")

            # Export report to CSV
            current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_name = f"revenue_report_{current_time}.csv"
            export_to_csv(df, report_name)

        else:
            print("No transactions found for the given period.")
        connection.close()
    else:
        print("Unable to generate report due to database connection issue.")

if __name__ == "__main__":
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    generate_revenue_report(start_date, end_date)