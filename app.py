import os
import google.generativeai as genai
import pandas as pd
import json
import logging
from datetime import datetime

# Setup Logging
logging.basicConfig(
    filename='bot_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
genai.configure(api_key="YOUR_API_KEY")

def run_recon():
    try:
        logging.info("Starting GSTR-1 Reconciliation process.")
        
        # 1. Identify files
        files_in_dir = os.listdir('.')
        pdf_files = [f for f in files_in_dir if f.lower().endswith('.pdf')]
        csv_files = [f for f in files_in_dir if f.lower().endswith('.csv')]

        if not pdf_files:
            raise FileNotFoundError("No PDF file found in the folder.")
        if not csv_files:
            raise FileNotFoundError("No CSV files found in the folder.")

        pdf_file_path = pdf_files[0]
        logging.info(f"Files detected: PDF={pdf_file_path}, CSV_Count={len(csv_files)}")

        # 2. Upload to Gemini
        print("Uploading files to Gemini API...")
        uploaded_pdf = genai.upload_file(path=pdf_file_path)
        uploaded_csvs = [genai.upload_file(path=f) for f in csv_files]

        # 3. Request JSON from Model
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = """
        Perform a GSTR-1 reconciliation. Compare PDF 'Booked Revenue Summary' 
        against CSV data. Return result ONLY as a JSON array:
        [{"Component": "...", "GSTR1_Excel": 0.0, "PDF_Export": 0.0, "Difference": 0.0, "Status": "..."}]
        """

        response = model.generate_content([prompt, uploaded_pdf, *uploaded_csvs])
        
        # 4. Process JSON and save to Excel
        raw_json = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(raw_json)
        
        df = pd.DataFrame(data)
        output_name = f"Recon_Result_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(output_name, index=False)
        
        logging.info(f"Successfully generated {output_name}")
        print(f"Success! Result saved in {output_name}")

    except Exception as e:
        logging.error(f"PROCESS FAILED: {str(e)}")
        print(f"ERROR: Check bot_log.txt for details. Message: {e}")

if __name__ == "__main__":
    run_recon()
