import csv

def read_columns(file_path):
    columns = {
        '<Mag. I1>': [],
        '<Phase I1>': [],
        '<Mag. Q1>': [],
        '<Phase Q1>': [],
        '<Mag. I2>': [],
        '<Phase I2>': [],
        '<Mag. Q2>': [],
        '<Phase Q2>': []
    }
    
    with open(file_path, 'r') as file:
        # Skip lines until the delimiter line is found
        for line in file:
            if line.strip() == '=======================================================':
                break
        
        # Read the header
        reader = csv.DictReader(file, delimiter='\t')
        
        # Print the column names to debug
        print("Column names in file:", reader.fieldnames)
        
        for row in reader:
            for col in columns:
                if col in row:
                    columns[col].append(row[col])
                else:
                    print(f"Warning: Column '{col}' not found in row.")
    
    return columns

if __name__ == '__main__':
    # Example usage
    file_path = 'radar_samples/FD/trial_2024-08-14_13-33-18.376.txt'
    data = read_columns(file_path)

    # Print the first few entries for each column
    for col, values in data.items():
        print(f"{col}: {values[:5]}")