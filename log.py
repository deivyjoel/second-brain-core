import logging
import sys

# Configuración básica de logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",  
    handlers=[
        logging.StreamHandler(sys.stdout),             
        logging.FileHandler("app.log", encoding="utf-8") 
    ]
)

# Obtén un logger con nombre (opcional, útil en proyectos grandes)
logger = logging.getLogger("MiApp")

# Ejemplos de uso
logger.info("Empezo la APP :)")

"""
Only saves information about changes to the database.
"""

