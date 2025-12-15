import requests
import pandas as pd
import math


# dataset_id = "def0a3ee-ce00-4bad-887f-3c78b2876969"  # Replace with the actual dataset ID
dataset_id = "f30cc8bc-8e97-449e-96a4-77b0400262d1"  # Replace with the actual dataset ID
base_url = f"https://api.stats.gov.wales/v1/{dataset_id}/view"
page_size = 100000 # Using a large page size as seen in previous successful attempts

all_data = []
page_number = 1
total_records = None

# First request to get total_records and initial data
url = f"{base_url}?page_number={page_number}&page_size={page_size}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    page_info = data.get('page_info')
    if page_info:
        total_records = page_info.get('total_records')
        print(f"Total number of records: {total_records}")
        all_data.extend(data.get('data', []))
        page_number += 1

        if total_records is not None and page_size is not None and page_size > 0:
            total_pages = math.ceil(total_records / page_size)

            # Loop through remaining pages
            while page_number <= total_pages:
                url = f"{base_url}?page_number={page_number}&page_size={page_size}"
                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json()
                    all_data.extend(data.get('data', []))
                    page_number += 1
                else:
                    print(f"Error fetching data from page {page_number}: {response.status_code}")
                    break # Stop fetching if there's an error

            if all_data:
                df_full_dataset = pd.DataFrame(all_data)
                print(f"Successfully fetched data from {len(all_data)} records across {page_number - 1} pages.")
                print(df_full_dataset.head())
                
                # Save to CSV
                output_filename = f"WIMD.csv"
                df_full_dataset.to_csv(output_filename, index=False)
                print(f"Data saved to: {output_filename}")
            else:
                print("No data fetched after pagination.")
        else:
            print("Could not calculate total pages for pagination. Check total_records and page_size from the initial request.")
    else:
        print("Page information not found in the initial dataset response.")

else:
    print(f"Error fetching data from the initial page: {response.status_code}")