import pdfplumber

pdf_name = "wars_2003-2019.pdf"
with pdfplumber.open(pdf_name) as pdf:
    pages = pdf.pages
    page_inspect = pages[0]  # Inspect the first page
            

    im = page_inspect.to_image()
    im.debug_tablefinder(table_settings={})
    im.save("debug_tablefinder.png")  # Save the debug image to a file