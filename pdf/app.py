import pdfplumber
import os

# Get current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Input PDF path (full path to your file)
pdf_path = r"C:\Users\Kavtech AI Engineer\Downloads\Projects\CAMMI\pdf\test_pdf.pdf"

# Output path in the same folder as app.py
output_path = os.path.join(current_dir, "output.txt")

with pdfplumber.open(pdf_path) as pdf:
    with open(output_path, "w", encoding="utf-8") as f:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=1)
            if text:
                f.write(text)
                f.write("\n" + "-" * 80 + "\n")
                print(text)

print("✅ Extraction complete! Text saved as:", output_path)
