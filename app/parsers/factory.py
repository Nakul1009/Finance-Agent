import os
from typing import List, Dict, Any
from app.parsers.csv_parser import CSVParser
from app.parsers.xlsx_parser import XLSXParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.ocr_parser import OCRParser

class DocumentParserFactory:
    @staticmethod
    def parse_document(file_path: str, filename: str) -> List[Dict[str, Any]]:
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.csv':
            parser = CSVParser()
            return parser.parse(file_path)
        elif ext in ['.xlsx', '.xls']:
            parser = XLSXParser()
            return parser.parse(file_path)
        elif ext == '.pdf':
            pdf_parser = PDFParser()
            txs = pdf_parser.parse(file_path)
            if not txs:
                # Fallback to OCR parser for scanned PDFs
                ocr_parser = OCRParser()
                txs = ocr_parser.parse(file_path)
            return txs
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
