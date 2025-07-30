import fitz  # PyMuPDF
import re
import pandas as pd
import logging
from typing import Dict, Optional, Tuple, Any

# Configure logger
logger = logging.getLogger(__name__)

def extract_pdf_data(url_bytes: Tuple[str, Any]) -> Tuple[str, Dict[str, Optional[str]]]:
    """
    Extract structured data from PDF content if it contains 'PACKAGE OPTION ADDENDUM'.

    Args:
        url_bytes (Tuple[str, BytesIO]): A tuple containing URL and PDF content as bytes or BytesIO.

    Returns:
        Tuple[str, Dict]: The URL and extracted dictionary mapping parts to temperatures.
    """
    url, byts = url_bytes

    if byts is None:
        logger.warning("Empty content received for URL: %s", url)
        return url, {}

    try:
        with fitz.open(stream=byts) as doc:
            results = {}
            for page in doc.pages():
                text = page.get_text()
                if "PACKAGE OPTION ADDENDUM" in text:
                    tables_data = _get_table(page)
                    results.update(_double_check_parts(tables_data, text))
            return url, results
    except Exception as e:
        logger.error("Error extracting PDF content for URL %s: %s", url, e, exc_info=True)
        return url, {}


def _double_check_parts(tables_data: Dict[str, Optional[str]], full_text: str) -> Dict[str, Optional[str]]:
    """
    Validates each part name exists in the full text using case-insensitive matching.

    Args:
        tables_data (Dict): Dictionary of {part: temp} from table extraction.
        full_text (str): Full raw text of the PDF page.

    Returns:
        Dict: Updated dict with matched or original part names.
    """
    results = {}
    full_text_lower = full_text.lower()

    for part, temp in tables_data.items():
        if not part:
            continue
        escaped_part = re.escape(part.strip())
        match = re.search(rf"\w*{escaped_part}\w*", full_text_lower, re.IGNORECASE)
        if match:
            matched_part = full_text[match.start():match.end()]
            results[matched_part] = temp
        else:
            results[part] = temp
    return results


def _get_table(page: fitz.Page) -> Dict[str, Optional[str]]:
    """
    Extracts the first column as parts and any op-temp column from the table.

    Args:
        page (fitz.Page): PDF page object.

    Returns:
        Dict: Dictionary of {part: temperature}.
    """
    results = {}
    try:
        tables = page.find_tables().tables
        for table in tables:
            df_table = table.to_pandas()
            if df_table.empty:
                continue

            # First column = part numbers
            parts_column = df_table.iloc[:, 0].astype(str).str.strip()
            if parts_column.dropna().empty:
                continue

            # Find op temp column
            temp_col_name = None
            for col in df_table.columns:
                if "op temp" in col.lower():
                    temp_col_name = col
                    break

            # Get temps
            if temp_col_name:
                temp_values = df_table[temp_col_name]
            else:
                temp_values = [None] * len(df_table)

            # Build result dict
            for part, temp in zip(parts_column, temp_values):
                results[part] = str(temp).strip() if pd.notna(temp) else None

    except Exception as e:
        logger.exception("Error processing table on page: %s", e)

    return results