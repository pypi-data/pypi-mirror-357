import os
import time
import subprocess
import tempfile
from PyPDF2 import PdfReader, PdfWriter

def slow_print(pdf_path: str, sumatra_path: str, printer_name: str = None, delay: int = 10):
    """
    Prints a PDF file one page at a time using SumatraPDF with a delay.

    Args:
        pdf_path (str): Full path to the PDF file to print.
        sumatra_path (str): Full path to SumatraPDF.exe.
        printer_name (str, optional): Name of the installed printer. Uses default if None.
        delay (int, optional): Delay in seconds between each page. Default is 10.
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"Total pages found: {total_pages}")

    with tempfile.TemporaryDirectory() as temp_dir:
        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])

            temp_pdf_path = os.path.join(temp_dir, f"page_{i + 1}.pdf")
            with open(temp_pdf_path, "wb") as f:
                writer.write(f)

            print(f"🖨️  Printing page {i + 1} of {total_pages}...")
            cmd = [sumatra_path]
            if printer_name:
                cmd += ["-print-to", printer_name]
            cmd.append(temp_pdf_path)
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

            if i < total_pages - 1:
                print(f"⏳ Waiting {delay} seconds...")
                time.sleep(delay)

    print("✅ All pages printed.")
