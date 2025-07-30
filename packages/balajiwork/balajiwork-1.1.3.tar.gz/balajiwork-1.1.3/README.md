# balajiwork

Utility functions for personal and professional use.

## Tools included:

### 🧾 ifc2xlsx
A GUI tool to convert IFC files to XLSX.

#### How to Run

You can launch the tool directly from the command line:

```cmd
ifc2xlsx
```

Or, if you have a Python script entry point:

```cmd
python -m balajiwork.ifc2xlsx
```

This will open the GUI window for selecting input and output directories and other options.

#### GUI Screenshot

![IFC to CSV Converter GUI](images/ifc2xlsx.png)

### 🖨️ slowprint
Prints a PDF file one page at a time with a delay using SumatraPDF to avoid printer jamming.

Usage:
```python
from balajiwork import slow_print

slow_print(
    pdf_path="C:\\pdf\\paper.pdf",
    sumatra_path="C:\\Tools\\SumatraPDF\\SumatraPDF.exe",
    printer_name="HP Smart Tank 660-670 series",
    delay=10
)
```
