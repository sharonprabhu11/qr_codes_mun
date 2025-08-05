import pandas as pd
import qrcode
import json
import random
import os
from PIL import Image

def generate_unique_code(committee: str, used_codes: set[str]) -> str:
    
    prefix = committee[:3].upper()
    
    while True:
        random_num = random.randint(100, 999)
        code = f"{prefix}{random_num}"
        if code not in used_codes:
            used_codes.add(code)
            return code

def create_qr_code(data: dict, filename: str) -> str:
    #generating qr code for given data
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename

def process_delegates(csv_file: str) -> None:
    
    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} delegates from CSV")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Create output directories
    os.makedirs('qr_codes', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    used_codes = set()
    results = []
    
    print("\n Generating codes and QR codes...")
    
    for index, row in df.iterrows():
        try:
            # Generate unique code
            committee = row.get('Committee', 'GEN')
            unique_code = generate_unique_code(committee, used_codes)
            
            # Create JSON data
            delegate_data = {
                "message": "message!",
                "name": row.get('Name', 'Unknown Delegate'),
                "code": unique_code,
                "committee": committee,
                "country": row.get('Country', 'Unknown')
            }
            
            # Generate QR code
            qr_filename = f"qr_codes/{unique_code}_{row.get('Name', 'unknown').replace(' ', '_')}.png"
            create_qr_code(delegate_data, qr_filename)
            
            # Store result
            result = {
                'Original_Name': row.get('Name'),
                'Original_Email': row.get('Email'),
                'Original_Committee': row.get('Committee'),
                'Original_Country': row.get('Country'),
                'Generated_Code': unique_code,
                'QR_Filename': qr_filename,
                'JSON_Data': json.dumps(delegate_data)
            }
            results.append(result)
            
            print(f"{unique_code} - {row.get('Name')} ({committee})")
            
        except Exception as e:
            print(f"Error processing {row.get('Name', 'unknown')}: {e}")
    
    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv('output/delegates_with_codes.csv', index=False)
    
    # Save JSON data
    json_data = [json.loads(result['JSON_Data']) for result in results]
    with open('output/all_delegates.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\n {len(results)} QR codes generated")

if __name__ == "__main__":
    
    csv_filename = 'delegates.csv'
    #can get that as input also
    process_delegates(csv_filename)