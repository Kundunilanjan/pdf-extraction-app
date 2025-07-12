import streamlit as st
import fitz  # PyMuPDF
import io
import os
import zipfile
import re
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

st.set_page_config(page_title="PDF Extractor by PyMuPDF", layout="wide")
st.title("📄 PDF Extractor – Metadata, Text, Links, TOC, Headers, Images")

uploaded_file = st.file_uploader("📤 Upload a PDF file", type=["pdf"])
MAX_HEADER_FOOTER_Y = 80  # Threshold in pixels from top/bottom to detect headers/footers

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.success(f"✅ PDF loaded successfully! Total Pages: {doc.page_count}")

    unique_images = {}
    toc_candidates = []
    extracted_pages = []

    # Create directory to store images and reconstructed files
    image_save_dir = "extracted_images"
    os.makedirs(image_save_dir, exist_ok=True)

    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text()
        links = page.get_links()
        blocks = page.get_text("blocks")
        page_height = page.rect.height
        embedded_images = page.get_images(full=True)

        toc_candidates.extend(page.get_text("text").splitlines())

        page_headers = []
        page_footers = []
        page_body = []

        for b in blocks:
            block_text = b[4].strip()
            y0 = b[1]
            y1 = b[3]
            if block_text:
                if y0 < MAX_HEADER_FOOTER_Y:
                    page_headers.append(block_text)
                elif y1 > page_height - MAX_HEADER_FOOTER_Y:
                    page_footers.append(block_text)
                else:
                    page_body.append(block_text)

        extracted_pages.append({
            "headers": page_headers,
            "body": page_body,
            "footers": page_footers
        })

        # Extract and save images
        for img_index, img in enumerate(embedded_images):
            xref = img[0]
            if xref not in unique_images:
                try:
                    base_image = doc.extract_image(xref)
                    img_data = base_image["image"]
                    ext = base_image["ext"]
                    filename = f"page_{i + 1}_img{img_index + 1}.{ext}"
                    filepath = os.path.join(image_save_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                    unique_images[xref] = filepath
                except Exception as e:
                    st.error(f"⚠️ Error extracting image on page {i + 1}: {e}")

        # ─── Per Page Display ─────────────────────────────
        st.markdown(f"---\n### 📄 Page {i + 1}")

        with st.expander("📑 Page Metadata"):
            metadata = {
                "Page Number": i + 1,
                "Size": f"{page.rect.width} x {page.rect.height}",
                "Rotation": page.rotation,
                "Text Length": len(text),
                "Number of Links": len(links),
                "Number of Embedded Images": len(embedded_images)
            }
            st.json(metadata)

        with st.expander("📝 Extracted Text"):
            if text.strip():
                st.text(text)
            else:
                st.warning("No text found on this page.")

        with st.expander("🔗 Page Links"):
            if links:
                for link in links:
                    st.json(link)
            else:
                st.caption("🔗 No links found on this page.")

        with st.expander("🧾 Headers & Footers"):
            if page_headers:
                st.markdown("**Headers:**")
                for h in page_headers:
                    st.markdown(f"- {h}")
            else:
                st.caption("No headers detected.")

            if page_footers:
                st.markdown("**Footers:**")
                for f in page_footers:
                    st.markdown(f"- {f}")
            else:
                st.caption("No footers detected.")

    # ─── TOC Detection ─────────────────────
    st.markdown("---")
    st.subheader("📌 Detected Table of Contents")
    pattern = re.compile(r"\.{2,}\s*\d+$")
    toc_lines = [line.strip() for line in toc_candidates if pattern.search(line.strip())]

    if toc_lines:
        with st.expander("📑 View TOC Entries"):
            for entry in toc_lines:
                st.markdown(f"• {entry}")
    else:
        st.info("No Table of Contents entries detected.")

    # ─── Download All Images as ZIP ─────────────────────
    st.markdown("---")
    st.header("📦 Download All Extracted Images")

    if unique_images:
        zip_path = os.path.join(image_save_dir, "all_images.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for path in unique_images.values():
                zipf.write(path, arcname=os.path.basename(path))
        with open(zip_path, "rb") as zip_file:
            st.download_button(
                label="⬇️ Download All Images as ZIP",
                data=zip_file,
                file_name="all_images.zip",
                mime="application/zip"
            )
    else:
        st.info("No embedded images found in the PDF.")

    # ─── Reconstruct PDF with ReportLab ─────────────────────
    st.markdown("---")
    st.header("🛠 Reconstruct PDF (Header → Content → Footer)")

    reconstructed_pdf_path = os.path.join(image_save_dir, "reconstructed.pdf")
    styles = getSampleStyleSheet()
    doc_out = SimpleDocTemplate(reconstructed_pdf_path, pagesize=A4)
    elements = []

    for i, page_content in enumerate(extracted_pages):
        headers = page_content["headers"]
        body = page_content["body"]
        footers = page_content["footers"]

        if headers:
            elements.append(Paragraph("<b>Header:</b>", styles["Heading4"]))
            for h in headers:
                elements.append(Paragraph(h, styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

        if body:
            elements.append(Paragraph("<b>Content:</b>", styles["Heading4"]))
            for para in body:
                elements.append(Paragraph(para, styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

        if footers:
            elements.append(Paragraph("<b>Footer:</b>", styles["Heading4"]))
            for f in footers:
                elements.append(Paragraph(f, styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

        elements.append(PageBreak())

    doc_out.build(elements)

    with open(reconstructed_pdf_path, "rb") as f:
        st.download_button(
            label="📄 Download Reconstructed PDF",
            data=f,
            file_name="reconstructed.pdf",
            mime="application/pdf"
        )

else:
    st.info("📤 Upload a PDF file to begin.")
