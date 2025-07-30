from .core import process_excel_with_pdfs
from .services.PDFParser import extract_pdf_data
from .services.ChunkService import process_pdf_chunks
from .utils.FileTools import FileTools
from .utils.DataUtils import expand_extracted_data

__version__ = "0.1.0"
__author__ = "Hamdi Emad"
__description__ = "A module for extracting data from PDFs linked in Excel files."