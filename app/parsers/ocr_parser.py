import fitz # PyMuPDF
from typing import List, Dict, Any
from app.parsers.pdf_parser import PDFParser

class OCRParser(PDFParser):
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        extracted_text = ""
        try:
            import pytesseract
            from PIL import Image
            import io

            doc = fitz.open(file_path)
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                text = pytesseract.image_to_string(img)
                extracted_text += text + "\n"
        except Exception:
            # Pytesseract or tesseract binary not available or failed
            return []

        if not extracted_text.strip():
            return []

        # Use PDFParser line regex engine on OCR extracted text
        return self._parse_text_lines(extracted_text)

    def _parse_text_lines(self, full_text: str) -> List[Dict[str, Any]]:
        # Temporary file mock or direct line regex logic from PDFParser
        lines = full_text.splitlines()
        transactions = []
        import re
        date_pattern = re.compile(r'(\d{1,2}[\/\-\.](?:\d{1,2}|[A-Za-z]{3})[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})')

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            date_match = date_pattern.search(line_str)
            if not date_match:
                continue

            raw_date = date_match.group(1)
            date_str = self.clean_date(raw_date)

            numbers = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2}|\d+\.\d{2})', line_str)
            if not numbers:
                continue

            amounts = [self.clean_amount(n) for n in numbers if self.clean_amount(n) > 0]
            if not amounts:
                continue

            amount = amounts[0]
            balance = amounts[1] if len(amounts) > 1 else None

            narration = date_pattern.sub('', line_str)
            for num_str in numbers:
                narration = narration.replace(num_str, '')
            narration = re.sub(r'\b(Cr|Dr|INR|USD|EUR)\b', '', narration, flags=re.IGNORECASE).strip()

            if not narration:
                narration = "Scanned Transaction"

            tx_type = "expense"
            if 'cr' in line_str.lower() or any(kw in narration.lower() for kw in ['salary', 'credit', 'deposit', 'received']):
                tx_type = "income"

            transactions.append({
                "date": date_str,
                "description": narration,
                "merchant": narration,
                "amount": round(amount, 2),
                "transaction_type": tx_type,
                "balance": round(balance, 2) if balance is not None else None,
                "reference": None
            })

        return transactions
