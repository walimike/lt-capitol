import csv
from typing import List

csv_file = None

def generate_csv_file(file_name:str, trades: List = [], csv_header: List = [], encoding:str = 'UTF8'):
    with open(f'{file_name}.csv', 'w', encoding='UTF8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_header)
        writer.writeheader()
        writer.writerows(trades)
        global csv_file
        csv_file = f.name
