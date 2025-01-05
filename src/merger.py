import argparse
from PyPDF2 import PdfMerger

def merge_pdfs(pdf_list, output):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output)
    merger.close()

def main():
    parser = argparse.ArgumentParser(description="Merge PDF files into a single PDF.")
    parser.add_argument("pdfs", nargs='+', help="List of PDF files to merge")
    parser.add_argument("-o", "--output", required=True, help="Output file name for the merged PDF")
    args = parser.parse_args()
    
    merge_pdfs(args.pdfs, args.output)

if __name__ == "__main__":
    main()