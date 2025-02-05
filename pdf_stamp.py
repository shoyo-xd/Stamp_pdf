import os
import fitz  # PyMuPDF
from PIL import Image

# Static folder paths
pdf_to_be_stamped = r"C:\PDF_stamp\Raw_PDF_Files"
stamped = r"C:\PDF_stamp\Stamped_PDF_Files"
merged = r"C:\PDF_stamp\Merged_PDF_File"
stamp_png = r"C:\PDF_stamp\Stamp_Image_png\stamp6high.png"  # Ensure this file exists in the directory

def add_stamp_to_pdf(pdf_path, stamp_path, output_path):
    """Add a stamp to a single PDF with adjustable margins."""
    # Open stamp image
    stamp_image = Image.open(stamp_path).convert("RGBA")

    # Desired stamp size in cm
    stamp_width_cm = 0.9
    stamp_height_cm = 0.8
    dpi = 300
    stamp_width_px = int(stamp_width_cm * dpi / 2.54)
    stamp_height_px = int(stamp_height_cm * dpi / 2.54)

    # Resize stamp image
    stamp_image = stamp_image.resize((stamp_width_px, stamp_height_px), Image.LANCZOS)

    # Temporary stamp file for overlay
    temp_stamp_path = os.path.join(os.path.dirname(output_path), "temp_stamp.png")
    stamp_image.save(temp_stamp_path, "PNG")

    # Open the PDF and add stamp to each page
    pdf_document = fitz.open(pdf_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        page_width = page.rect.width
        page_height = page.rect.height

        # Margins
        margin_top = 10
        margin_right = 30
        margin_bottom = 50
        margin_left = 10

        # Position the stamp (bottom-right corner with margins by default)
        x_position = page_width - stamp_width_px - margin_right
        y_position = page_height - stamp_height_px - margin_bottom

        # Insert image stamp on each page
        page.insert_image(
            fitz.Rect(
                x_position, 
                y_position, 
                x_position + stamp_width_px, 
                y_position + stamp_height_px
            ),
            filename=temp_stamp_path,
            overlay=True,
        )

    # Save the stamped PDF and remove temp stamp
    pdf_document.save(output_path)
    pdf_document.close()
    os.remove(temp_stamp_path)

    print(f"Stamped PDF saved to: {output_path}")

def stamp_all_pdfs_in_folder(folder_path, stamp_path, output_folder):
    """Stamp all PDFs in a folder and save to output folder."""
    os.makedirs(output_folder, exist_ok=True)
    stamped_pdfs = []

    pdf_files = [filename for filename in os.listdir(folder_path) if filename.endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in the folder: {folder_path}")
        return stamped_pdfs

    for filename in pdf_files:
        pdf_path = os.path.join(folder_path, filename)
        output_path = os.path.join(output_folder, filename)
        try:
            print(f"Stamping: {pdf_path}")
            add_stamp_to_pdf(pdf_path, stamp_path, output_path)
            stamped_pdfs.append(output_path)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

    return stamped_pdfs

def merge_pdfs(pdf_list, output_path):
    """Merge multiple PDFs into one."""
    merged_pdf = fitz.open()

    for pdf_path in pdf_list:
        pdf = fitz.open(pdf_path)
        merged_pdf.insert_pdf(pdf)
        pdf.close()

    if len(merged_pdf) == 0:
        print("No pages to merge in the final PDF.")
        return

    merged_pdf.save(output_path)
    merged_pdf.close()

    print(f"Merged PDF saved to: {output_path}")

def main():
    # Ensure the directories exist
    if not all(os.path.exists(path) for path in [pdf_to_be_stamped, stamp_png, stamped, merged]):
        print("One or more directories do not exist. Please check the paths.")
        return

    # Process PDFs
    stamped_pdfs = stamp_all_pdfs_in_folder(pdf_to_be_stamped, stamp_png, stamped)

    if not stamped_pdfs:
        print("No PDFs to merge. Exiting.")
        return

    # Merge stamped PDFs into one
    merged_output_path = os.path.join(merged, "merged_stamped.pdf")
    try:
        merge_pdfs(stamped_pdfs, merged_output_path)
    except Exception as e:
        print(f"Error merging PDFs: {e}")

if __name__ == "__main__":
    main()
