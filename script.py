from datetime import datetime
from collections import defaultdict
import os

#Each transactions store information on a line in a comma seperated format, I need to parse each transaction into a format convenient to work with 
def parser(line):
    try:
        partition = line.strip().split(',')
        staff_id = int(partition[0])
        time_str = partition[1]
        products_str = partition[2][1:-1]
        sale_amount = float(partition[3])
        
        # parsing the transaction time using the datetime module imported above
        transaction_time = datetime.fromisoformat(time_str)
        
        # parsing the products
        products = {}
        for item in products_str.split('|'):
            if ':' in item:
                product_id, quantity = item.split(':')
                products[int(product_id)] = int(quantity)
        
        return staff_id, transaction_time, products, sale_amount
    except Exception as e:
        print(f"Error parsing line: {line}. Error: {e}")
        return None

def Transaction(folder_path):
    daily_total_products = defaultdict(int)
    daily_total_sales = defaultdict(float)
    product_volume = defaultdict(int)
    monthly_staff_sales = defaultdict(lambda: defaultdict(float))
    hourly_transaction_volume = defaultdict(lambda: defaultdict(int))
    hourly_transaction_count = defaultdict(int)
    
    #Folders containing numerous files were given as test cases, each file contains transactions for a day
    #first, i have to iterate through that folder to get each file
    transaction_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    if not transaction_files:
        print(f"No transaction files found in {folder_path}!")
        return

    #I also have to iterate through each file and read each line
    for file_name in transaction_files:
        date = file_name.split('.')[0]
        daily_total_products[date] = 0
        daily_total_sales[date] = 0.0
        
        with open(os.path.join(folder_path, file_name), 'r') as file:
            for line in file:
                parsed = parser(line)
                if not parsed:
                    continue
                
                #Destructure the properties from the parsed data helper function
                staff_id, transaction_time, product_quantities, sale_amount = parsed
                
                # Update daily totals
                total_products = sum(product_quantities.values())
                daily_total_products[date] += total_products
                daily_total_sales[date] += sale_amount
                
                #As seen in the files given, in a transaction, there can be multiple products, iterating over the transaction and updatng the total quantity sold
                for product_id, quantity in product_quantities.items():
                    product_volume[product_id] += quantity
                
                # To get the monthly top staff
                month_key = transaction_time.strftime('%Y-%m')
                monthly_staff_sales[month_key][staff_id] += sale_amount
                
                
                hour_key = transaction_time.hour #The dot operator can be used on transaction_time since it is in datetime format
                hourly_transaction_volume[hour_key][date] += total_products
                hourly_transaction_count[hour_key] += 1


    if not daily_total_products:
        print(f"No transactions found in {folder_path}!")
        return

    # To get the day with the highest sales volume
    max_volume_day = max(daily_total_products, key=lambda k: daily_total_products[k])
    max_volume = daily_total_products[max_volume_day]

    # To get the day with the highest sales value
    max_sales_day = max(daily_total_sales, key=lambda k: daily_total_sales[k])
    max_sales = daily_total_sales[max_sales_day]

    # To find the product with the highest value in product sales
    most_sold_product = max(product_volume, key=lambda k: product_volume[k])
    most_sold_quantity = product_volume[most_sold_product]

    # For each month, find the staff member with the highest sale value
    top_staff_by_month = {}
    for month, staff_sales in monthly_staff_sales.items():
        top_staff_by_month[month] = max(staff_sales, key=lambda k: staff_sales[k])

    # Find the  highest hour by average transaction volume
    hourly_avg_volume = {}
    for hour, volume_dict in hourly_transaction_volume.items():
        total_products = sum(volume_dict.values())
        total_transactions = hourly_transaction_count[hour]
        hourly_avg_volume[hour] = total_products / total_transactions

    if hourly_avg_volume:
        best_hour = max(hourly_avg_volume, key=lambda k: hourly_avg_volume[k])
        best_avg_volume = hourly_avg_volume[best_hour]
    else:
        best_hour, best_avg_volume = None, 0

    # Printing the results with the aid of a formtted string
    print(f"Results for {folder_path}") # For outlining the individual results of each folder depending on the folder structure for each of them
    print(f"1. Highest sales volume in a day: {max_volume} products on {max_volume_day}")
    print(f"2. Highest sales value in a day: ${max_sales:.2f} on {max_sales_day}")
    print(f"3. Most sold product by volume: Product ID {most_sold_product} with {most_sold_quantity} units sold")
    print("4. Highest sales staff by month:")
    for month, staff in top_staff_by_month.items():
        print(f"   {month}: Staff ID {staff}")
    if best_hour is not None:
        print(f"5. Highest hour of the day by average transaction volume: {best_hour}:00 with an average of {best_avg_volume:.2f} products per transaction")
    else:
        print("5. No hourly data available.")

# The folder containing all the test cases given is in my project directory(mp-hackathon)
# Processing each test case folder 
if __name__ == "__main__":
    test_case_folders = [
        "mp-hackathon-sample-data/test-case-1",
        "mp-hackathon-sample-data/test-case-2",
        "mp-hackathon-sample-data/test-case-3",
        "mp-hackathon-sample-data/test-case-4",
        "mp-hackathon-sample-data/test-case-5",
    ]

    for test_folder in test_case_folders:
        print(f"\nAnalyzing folder: {test_folder}")
        Transaction(test_folder)