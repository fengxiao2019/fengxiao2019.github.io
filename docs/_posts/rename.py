import os
import re
import random
from datetime import datetime, timedelta

def sanitize_filename(filename):
    return filename.replace("'", "").replace(" ", "")

def strip_date(filename):
    return re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)

def random_date(start_year=2019, end_year=2022):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)

    time_between_dates = end_date - start_date
    random_number_of_days = random.randrange(time_between_dates.days)
    random_date = start_date + timedelta(days=random_number_of_days)

    return random_date.strftime('%Y-%m-%d')

# specify directory
directory = '.'

for dirpath, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        if filename.endswith('.md'):
            sanitized_filename = sanitize_filename(filename)
            sanitized_filename_without_date = strip_date(sanitized_filename)
            new_filename = f"{random_date()}-{sanitized_filename_without_date}"
            source = os.path.join(dirpath, filename)
            destination = os.path.join(dirpath, new_filename)
            os.rename(source, destination)
            print(f'Renamed file {source} to {destination}')
