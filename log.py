import logging
import sys

# Config basic log
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",  
    handlers=[        
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout) # <--- For the terminal
    ]
)

logger = logging.getLogger("MiApp")
logger.info("Start the APP :)")

"""
Logs only persistence-related events and database state changes.
Application-level errors and internal exceptions are handled elsewhere.
"""

