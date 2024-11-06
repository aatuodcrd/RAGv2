import os
import pandas as pd
from unidecode import unidecode

def sanitize_filename(filename):
    # Replace spaces with underscores and remove any problematic characters
    return filename.replace(" ", "_")

def convert_excel_to_csv(uploaded_file, temp_dir, file_name):
    output_filename_list = []
    try:
        xls = pd.ExcelFile(uploaded_file)
        base_filename = sanitize_filename(os.path.splitext(unidecode(uploaded_file.name))[0])

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

            # Preprocess the DataFrame to remove rows with all null values
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', axis=1, inplace=True)
            sanitized_sheet_name = unidecode(sanitize_filename(sheet_name))
            csv_filename = f"{base_filename}_{file_name}_{sanitized_sheet_name}.csv"
            csv_filepath = os.path.join(temp_dir, csv_filename)
            df.to_csv(csv_filepath, index=False)
            output_filename_list.append(csv_filename)
    except Exception as e:
        print(f"Error processing Excel file {uploaded_file.name}: {str(e)}")
    return output_filename_list

def preprocess_csv(uploaded_file, temp_dir):
    output_filename = sanitize_filename(uploaded_file)
    csv_filepath = os.path.join(temp_dir, output_filename)

    try:
        df = pd.read_csv(csv_filepath)

        # Preprocess the DataFrame to remove rows with all null values
        df.dropna(how='all', inplace=True)
        df.dropna(how='all', axis=1, inplace=True)
        df.to_csv(csv_filepath, index=False)
    except Exception as e:
        print(f"Error processing CSV file {uploaded_file}: {str(e)}")
    return output_filename