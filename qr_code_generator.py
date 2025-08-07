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
    img = img.resize((700, 700))
    
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
    os.makedirs('id_cards', exist_ok=True) 
    
    used_codes = set()
    results = []
    id_card_template = "/home/sharonprabhu/backup/college/ssn_snuc_mun_25/qr_codes/IDCard.png"
    
    print("\n Generating codes and QR codes...")
    
    for index, row in df.iterrows():
        try:
            # Generate unique code
            committee = row.get('Committee', 'GEN')
            unique_code = generate_unique_code(committee, used_codes)
            food_preference = row.get('Food Preference', 'Not Specified')
            
            # Create JSON data
            delegate_data = {
                "message": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "name": row.get('Name', 'Unknown'),
                "code": unique_code,
                "committee": committee,
                "country": row.get('Country', 'Unknown'),
                "food preference": food_preference
            }
            
            qr_data = {
                "message": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "name": row.get('Name', 'Unknown'),
                "code": unique_code     
            }
            
            # Generate QR code
            qr_filename = f"qr_codes/{unique_code}.png"
            create_qr_code(qr_data, qr_filename)
            
            # Create ID card with QR code
            template = Image.open(id_card_template)
            qr_img = Image.open(qr_filename)
            
         
            template.paste(qr_img, (200, 500))  
            id_card_filename = f"id_cards/{unique_code}_id_card.png"
            template.save(id_card_filename)
            
            # Store result
            result = {
                'Original_Name': row.get('Name'),
                'Original_Email': row.get('Email'),
                'Original_Committee': row.get('Committee'),
                'Original_Country': row.get('Country'),
                'Generated_Code': unique_code,
                'QR_Filename': qr_filename,
                'ID_Card_Filename': id_card_filename,
                'JSON_Data': json.dumps(delegate_data)
            }
            results.append(result)
            
            print(f"{unique_code} - {row.get('Name')} ({committee}) - ID card created")
            
        except Exception as e:
            print(f"Error processing {row.get('Name', 'unknown')}: {e}")
    
    # Add 'code' column to original dataframe and save as results.csv
    df['code'] = [r['Generated_Code'] for r in results]
    df.to_csv('output/results.csv', index=False)
    
    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv('output/delegates_with_codes.csv', index=False)
    
    # Save JSON data
    json_data = [json.loads(result['JSON_Data']) for result in results]
    with open('output/all_delegates.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\n {len(results)} QR codes and ID cards generated")

if __name__ == "__main__":
    
    csv_filename = 'delegates.csv'
    #can get that as input also
    process_delegates(csv_filename)