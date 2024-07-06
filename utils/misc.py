import csv
import os
import hashlib


def csv_init(file_name, header_row=None):
    csv_file = file_name
    csv_path = os.path.join(os.getcwd(), csv_file)

    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            if header_row:
                writer.writerow(header_row)
        print(f"The CSV file '{csv_file}' has been created.")
    else:
        print(f"The CSV file '{csv_file}' already exists.")


def generate_hash(data):
    hash_object = hashlib.new('md5')
    hash_object.update(data.encode('utf-8'))
    return hash_object.hexdigest()
