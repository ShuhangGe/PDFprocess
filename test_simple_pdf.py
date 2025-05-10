import fpdf

def create_simple_pdf(output_file):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="This is a simple test PDF", ln=1, align="C")
    pdf.cell(200, 10, txt="Testing PDF extraction", ln=1, align="C")
    pdf.output(output_file)

if __name__ == "__main__":
    create_simple_pdf("test.pdf")
    print("Created test.pdf") 