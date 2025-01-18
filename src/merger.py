import argparse
from PyPDF2 import PdfReader, PdfWriter

def merge_pdfs(input_paths, output_path, pages):
    pdf_writer = PdfWriter()
    for path, pgs in zip(input_paths, pages):
        pdf_reader = PdfReader(path)
        for page in range(len(pdf_reader.pages)):
            if pgs == "All" or page in pgs:
                pdf_writer.add_page(pdf_reader.pages[page])
    with open(output_path, 'wb') as fh:
        pdf_writer.write(fh)

def main():
    parser = argparse.ArgumentParser(description="Merge PDF files into a single PDF.")
    parser.add_argument("pdfs", nargs='+', help="List of PDF files to merge")
    parser.add_argument("-o", "--output", required=True, help="Output file name for the merged PDF")
    args = parser.parse_args()
    
    merge_pdfs(args.pdfs, args.output)

if __name__ == "__main__":
    main()