from concurrent.futures import ProcessPoolExecutor
from typing import List, Tuple, Dict, Any, Optional
import logging

from Texas_Extraction.services.ChunkProcessor import ChunkProcessor
from Texas_Extraction.helper.config import Settings

# Configure logger
logger = logging.getLogger(__name__)

class MainProcessor:
    def __init__(self, urls: List[str]):
        """
        Initializes the processor with a list of URLs to process.

        Args:
            urls (List[str]): List of PDF URLs.
        """
        self.urls = urls
        self.chunk_size = Settings.CHUNK_SIZE.value
        self.chunks = self._chunk_urls()

    def _chunk_urls(self) -> List[List[str]]:
        """
        Splits the URL list into smaller chunks for parallel processing.

        Returns:
            List[List[str]]: A list of URL chunks.
        """
        logger.info(f"Splitting {len(self.urls)} URLs into chunks of {self.chunk_size}.")
        return [
            self.urls[i:i + self.chunk_size]
            for i in range(0, len(self.urls), self.chunk_size)
        ]

    def process_chunks(self) -> List[List[Tuple[str, Dict[str, Optional[str]]]]]:
        """
        Processes each chunk in parallel using multiprocessing.

        Returns:
            List of parsed results per chunk. Each result is a list of (url, data) tuples.
        """
        if not self.chunks:
            logger.warning("No chunks to process.")
            return []

        logger.info(f"Starting parallel processing of {len(self.chunks)} chunks.")

        with ProcessPoolExecutor(max_workers=Settings.MAX_MAIN_PROCESSES.value) as executor:
            results = list(executor.map(self._process_single_chunk, self.chunks))

        logger.info(f"Finished processing all chunks. Total chunks processed: {len(results)}.")
        return results

    def _process_single_chunk(self, chunk: List[str]) -> List[Tuple[str, Dict[str, Optional[str]]]]:
        """
        Process a single chunk of URLs using ChunkProcessor.

        Args:
            chunk (List[str]): A list of URLs.

        Returns:
            List of (url, data) results.
        """
        logger.debug(f"Processing chunk with {len(chunk)} URLs.")
        try:
            return ChunkProcessor().get_chunk_data(chunk)
        except Exception as e:
            logger.error(f"Error processing chunk: {e}", exc_info=True)
            return []