from enum import Enum
from os import getlogin

class Settings(Enum):

    CHUNK_SIZE = 10              # Number of URLs per chunk
    MAX_THREADS = 20              # Download threads
    MAX_POOLS = 4                 # Parsing processes
    MAX_MAIN_PROCESSES = 2        # Chunk-level parallelism

    LOG_FILE = r"C:\Users\{}\Documents\logger.log".format(getlogin())