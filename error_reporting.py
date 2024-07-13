import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)

def report_error(message: str, exception: Exception):
    logger.error(f"{message}: {exception}", exc_info=True)
    messagebox.showerror("Error", f"{message}: {exception}")
