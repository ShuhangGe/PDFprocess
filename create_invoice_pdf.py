import fpdf

def create_invoice_pdf(output_file):
    # Create a PDF object
    pdf = fpdf.FPDF()
    pdf.add_page()
    
    # Set up the PDF
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "INVOICE", 0, 1, "C")
    pdf.ln(10)
    
    # Company information
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "ACME Corporation", 0, 0)
    pdf.cell(90, 10, "Invoice #: INV-001", 0, 1, "R")
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 5, "123 Business Street", 0, 0)
    pdf.cell(90, 5, "Date: 2023-05-10", 0, 1, "R")
    pdf.cell(100, 5, "City, State 12345", 0, 0)
    pdf.cell(90, 5, "Due Date: 2023-06-10", 0, 1, "R")
    pdf.cell(100, 5, "Phone: (123) 456-7890", 0, 1)
    pdf.ln(10)
    
    # Customer information
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Bill To:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 5, "Customer Name", 0, 1)
    pdf.cell(190, 5, "Customer Company", 0, 1)
    pdf.cell(190, 5, "123 Customer Street", 0, 1)
    pdf.cell(190, 5, "City, State 54321", 0, 1)
    pdf.ln(10)
    
    # Invoice table header
    pdf.set_font("Arial", "B", 10)
    pdf.cell(10, 10, "#", 1, 0, "C")
    pdf.cell(80, 10, "Description", 1, 0, "C")
    pdf.cell(25, 10, "Qty", 1, 0, "C")
    pdf.cell(35, 10, "Unit Price", 1, 0, "C")
    pdf.cell(40, 10, "Amount", 1, 1, "C")
    
    # Invoice items
    pdf.set_font("Arial", "", 10)
    
    # Item 1
    pdf.cell(10, 10, "1", 1, 0, "C")
    pdf.cell(80, 10, "Product A", 1, 0)
    pdf.cell(25, 10, "2", 1, 0, "C")
    pdf.cell(35, 10, "$100.00", 1, 0, "R")
    pdf.cell(40, 10, "$200.00", 1, 1, "R")
    
    # Item 2
    pdf.cell(10, 10, "2", 1, 0, "C")
    pdf.cell(80, 10, "Service B", 1, 0)
    pdf.cell(25, 10, "5", 1, 0, "C")
    pdf.cell(35, 10, "$75.50", 1, 0, "R")
    pdf.cell(40, 10, "$377.50", 1, 1, "R")
    
    # Item 3
    pdf.cell(10, 10, "3", 1, 0, "C")
    pdf.cell(80, 10, "Product C", 1, 0)
    pdf.cell(25, 10, "1", 1, 0, "C")
    pdf.cell(35, 10, "$250.00", 1, 0, "R")
    pdf.cell(40, 10, "$250.00", 1, 1, "R")
    
    # Totals
    pdf.cell(115, 10, "", 0, 0)
    pdf.cell(35, 10, "Subtotal", 1, 0)
    pdf.cell(40, 10, "$827.50", 1, 1, "R")
    
    pdf.cell(115, 10, "", 0, 0)
    pdf.cell(35, 10, "Tax (10%)", 1, 0)
    pdf.cell(40, 10, "$82.75", 1, 1, "R")
    
    pdf.cell(115, 10, "", 0, 0)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(35, 10, "Total", 1, 0)
    pdf.cell(40, 10, "$910.25", 1, 1, "R")
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 10, "Thank you for your business!", 0, 1, "C")
    
    # Output the PDF
    pdf.output(output_file)
    print(f"Created invoice PDF: {output_file}")

if __name__ == "__main__":
    create_invoice_pdf("invoice.pdf") 