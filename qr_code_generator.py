import pandas as pd
import qrcode
import json
import random
from PIL import Image
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("output") #using pathlib for cross-platform compatibility
QR_CODES_DIR = OUTPUT_DIR / "qr_codes"
ID_CARDS_DIR = OUTPUT_DIR / "id_cards"

QR_CODE_SIZE = (700, 700)
QR_CODE_POSITION = (99, 422)

ID_CARD_TEMPLATE = "IDCard.png"
DEFAULT_CSV_FILE = "sample.csv"


class QRGenerator:
    
    def __init__(self):
        self.used_codes = set()
        self._setup_directories() # the '_' indicates that this is a private method
    
    def _setup_directories(self) -> None:
        for directory in [OUTPUT_DIR, QR_CODES_DIR, ID_CARDS_DIR]:
            directory.mkdir(exist_ok = True)    
    

    def _generate_unique_code(self, committee: str) -> str:
        """
        Generates a unique 6-character code by combining the first 3 letters of the committee name 
        with a random 3-digit number, ensuring no duplicates by checking against previously used codes.
        """
        
        prefix = committee[:3].upper()
        
        while True:
            random_num = random.randint(1000, 9999)
            code = f"{prefix}{random_num}"
            if code not in self.used_codes:
                self.used_codes.add(code)
                return code

    def _create_qr_code(self, data: dict) -> str:
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
        img = img.resize(QR_CODE_SIZE)
        
        filename = QR_CODES_DIR / f"{data['code']}.png"
        img.save(filename)
        return filename
    
    def _create_id_card(self, qr_path: Path ,code: str) -> Path:
        
        if not Path(ID_CARD_TEMPLATE).exists():
            raise FileNotFoundError(f"Template {ID_CARD_TEMPLATE} not found")
        
        template = Image.open(ID_CARD_TEMPLATE)
        qr_image = Image.open(qr_path)
        
        template.paste(qr_image, QR_CODE_POSITION)
        
        id_card_path = ID_CARDS_DIR / f"{code}.png"
        template.save(id_card_path)
        return id_card_path
    
    def _create_delegate_data(self, row: pd.Series, code: str) -> dict[str]:
        """Create comprehensive delegate data dictionary."""
        return {
            "message": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "name": row.get('Name', 'Unknown'),
            "code": code,
            "committee": row.get('Allotment', 'GEN'),
            "country": row.get('Country', 'Unknown'),
            "food_preference": row.get('Food Preference', 'Not Specified')
        }
    
    def _create_qr_data(self, row: pd.Series, code: str) -> dict[str, str]:
        """Create QR code specific data dictionary."""
        return {
            "name": row.get('Name', 'Unknown'),
            "code": code,
            "message": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
    
    def process_delegates(self, csv_file: str) -> None:
        """
        Process all delegates from CSV file - generate codes, QR codes, and ID cards.
        """
        
        try:
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded {len(df)} delegates from CSV")
        except FileNotFoundError:
            logger.error(f"CSV file '{csv_file}' not found")
            return
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return
        
        if df.empty:
            logger.warning("CSV file is empty")
            return
        
        logger.info("Generating codes and QR codes...")
        results = []
        
        # Process each delegate
        for index, row in df.iterrows():
            try:
                
                committee = row.get('Allotment', 'GEN')
                code = self._generate_unique_code(committee)
              
                delegate_data = self._create_delegate_data(row, code)
                qr_data = self._create_qr_data(row, code)
                
                qr_path = self._create_qr_code(qr_data)
                id_card_path = self._create_id_card(qr_path, code)
               
                result = {
                    'Original_Name': row.get('Name'),
                    'Original_Email': row.get('Email'),
                    'Original_Committee': row.get('Allotment'),
                    'Original_Country': row.get('Country'),
                    'Generated_Code': code,
                    'QR_Filename': str(qr_path),
                    'ID_Card_Filename': str(id_card_path),
                    'JSON_Data': json.dumps(delegate_data)
                }
                results.append(result)
                
                logger.info(f"{code} - {row.get('Name')} ({committee}) - ID card created")
                
            except Exception as e:
                logger.error(f"Error processing {row.get('Name', 'unknown')}: {e}")
                continue
        
        # Save all results
        if results:
            df['code'] = [r['Generated_Code'] for r in results]
            df.to_csv(OUTPUT_DIR / 'results.csv', index=False)
            
            results_df = pd.DataFrame(results)
            results_df.to_csv(OUTPUT_DIR / 'delegates_with_codes.csv', index=False)
            
            # Save JSON data
            json_data = [json.loads(result['JSON_Data']) for result in results]
            with open(OUTPUT_DIR / 'all_delegates.json', 'w') as f:
                json.dump(json_data, f, indent=2)
            
            logger.info(f"{len(results)} QR codes and ID cards generated successfully")
        else:
            logger.warning("No delegates were processed successfully")
    



def main():
    generator = QRGenerator()
    generator.process_delegates(DEFAULT_CSV_FILE)


if __name__ == "__main__":
    main()
