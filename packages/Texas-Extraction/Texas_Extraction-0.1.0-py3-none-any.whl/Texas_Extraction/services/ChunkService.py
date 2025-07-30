from Texas_Extraction.services.MainProcessor import MainProcessor
from typing import List, Tuple, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def process_pdf_chunks(urls: List[str]) -> Optional[List[List[Tuple[str, Dict]]]]:
    try:
        main_processor = MainProcessor(urls=urls)
        results = main_processor.process_chunks()
        logger.info("Finished processing all PDFs.")
        return results
    except Exception as e:
        logger.error(f"Error during PDF processing: {e}", exc_info=True)
        return None