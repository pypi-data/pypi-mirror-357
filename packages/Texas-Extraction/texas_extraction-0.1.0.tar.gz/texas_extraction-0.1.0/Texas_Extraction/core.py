# your_module_name/core.py

import logging
import time

from Texas_Extraction.utils.DataUtils import extract_unique_urls, merge_results_into_dataframe, expand_extracted_data
from Texas_Extraction.utils.FileTools import FileTools
from Texas_Extraction.services.ChunkService import process_pdf_chunks

logger = logging.getLogger(__name__)

def process_excel_with_pdfs(file_path: str):
    """
    End-to-end pipeline to read Excel file, download PDFs, extract data, and save output.

    Args:
        file_path (str): Path to input Excel file.
    
    Returns:
        pd.DataFrame: Final DataFrame with exploded parts and temps.
    """
    logger.info(f"Starting processing for file: {file_path}")
    start_time = time.time()

    # Step 1: Load input data
    file_tools = FileTools(file_path)
    df = file_tools.read()
    logger.info(f"Loaded DataFrame with {len(df)} rows.")

    # Step 2: Extract unique URLs
    urls = extract_unique_urls(df)
    if not urls:
        logger.warning("No valid URLs found in the file.")
        return df  # or raise exception depending on use case

    # Step 3: Process PDF chunks
    results = process_pdf_chunks(urls)
    if not results:
        logger.warning("No results returned from PDF processing.")
        return df

    # Step 4: Merge results back into DataFrame
    updated_df = merge_results_into_dataframe(df, results)

    # Step 5: Expand dictionary into parts and temps
    exploded_df = expand_extracted_data(updated_df)

    # Step 6: Save output
    file_tools.export_to_txt(exploded_df)

    end_time = time.time() - start_time
    running_time = format_duration(end_time)
    logger.info(f"Results successfully saved. Total time: {running_time}")

    return exploded_df


def format_duration(seconds: float) -> str:
    """Formats seconds into HH:MM:SS."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"