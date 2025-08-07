import pandas as pd
import qrcode
import json
import random
import os
from PIL import Image

def generate_unique_code(committee: str, used_codes: set[str]) -> str:
    """
    Generates a unique 6-character code by combining the first 3 letters of the committee name 
    with a random 3-digit number, ensuring no duplicates by checking against previously used codes.
    """
    
    prefix = committee[:3].upper()
    
    while True:
        random_num = random.randint(100, 999)
        code = f"{prefix}{random_num}"
        if code not in used_codes:
            used_codes.add(code)
            return code

def create_qr_code(data: dict, filename: str) -> str:
    """
    Creates a QR code from dictionary data by converting it to JSON, generating the QR code image,
    resizing it to 700x700 pixels, and saving it to the specified filename.
    """
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
    """
    Reads delegate information from CSV file, generates unique codes and QR codes for each delegate,
    creates personalized ID cards by pasting QR codes onto a template, and saves all outputs 
    (individual QR codes, ID cards, CSV results, and JSON data) to organized folders.
    """
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} delegates from CSV")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
   
    os.makedirs('qr_codes', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    os.makedirs('id_cards', exist_ok=True) 
    
    used_codes = set()
    results = []
    id_card_template = "IDCard.png"
    
    print("\n Generating codes and QR codes...")
    
    for index, row in df.iterrows():
        try:
    
            committee = row.get('Committee', 'GEN')
            unique_code = generate_unique_code(committee, used_codes)
            food_preference = row.get('Food Preference', 'Not Specified')
           
            delegate_data = {
                "message": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "name": row.get('Name', 'Unknown'),
                "code": unique_code,
                "committee": committee,
                "country": row.get('Country', 'Unknown'),
                "food preference": food_preference
            }
            
            qr_data = {
               
                "name": row.get('Name', 'Unknown'),
                "code": unique_code,
                "message": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",    
            }
            
            qr_filename = f"qr_codes/{unique_code}.png"
            create_qr_code(qr_data, qr_filename)
            
          
            template = Image.open(id_card_template)
            qr_img = Image.open(qr_filename)
            
         
            template.paste(qr_img, (99, 422))  
            id_card_filename = f"id_cards/{unique_code}.png"
            template.save(id_card_filename)
            
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
   
    df['code'] = [r['Generated_Code'] for r in results]
    df.to_csv('output/results.csv', index=False)
    
 
    results_df = pd.DataFrame(results)
    results_df.to_csv('output/delegates_with_codes.csv', index=False)
    
   
    json_data = [json.loads(result['JSON_Data']) for result in results]
    with open('output/all_delegates.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\n {len(results)} QR codes and ID cards generated")

if __name__ == "__main__":
    
    csv_filename = 'delegates.csv'
    process_delegates(csv_filename)