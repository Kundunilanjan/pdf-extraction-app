import streamlit as st
import fitz  # PyMuPDF
import spacy
import re
import os
import zipfile
import io
import pandas as pd
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# -------------------------- SETTINGS --------------------------
st.set_page_config(page_title="PDF Extractor by PyMuPDF", layout="wide")
st.title("📄 PDF Extractor – Metadata, TOC, Text, Links, Images, Rebuild")

MAX_HEADER_FOOTER_Y = 90
nlp = spacy.load("en_core_web_sm")

uploaded_file = st.file_uploader("📤 Upload a PDF file", type=["pdf"])

# -------------------------- FUNCTIONS --------------------------

def extract_toc_text(pdf_doc, max_pages=30):
    toc_text = ""
    for page_num in range(min(len(pdf_doc), max_pages)):
        page = pdf_doc[page_num]
        text = page.get_text()
        if "Contents" in text or "Table of Contents" in text:
            toc_text += "\n" + text
    return toc_text

def parse_toc_lines(raw_text):
    lines = raw_text.split("\n")
    toc_entries = []
    toc_pattern = re.compile(r"^(.*?)\s+(\d{1,4})$")

    for line in lines:
        line = line.strip()
        if not line or not any(char.isdigit() for char in line):
            continue
        match = toc_pattern.match(line)
        if match:
            title = match.group(1).strip().replace(" .", ".")
            page = int(match.group(2))
            toc_entries.append({"Title": title, "Page": page})
    return toc_entries

# -------------------------- MAIN LOGIC --------------------------

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.success(f"✅ PDF loaded successfully! Total Pages: {doc.page_count}")

    unique_images = {}
    extracted_pages = []
    all_text_lines = []

    image_save_dir = "extracted_images"
    os.makedirs(image_save_dir, exist_ok=True)

    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text()
        links = page.get_links()
        blocks = page.get_text("blocks")
        page_height = page.rect.height
        images = page.get_images(full=True)

        all_text_lines.extend(text.splitlines())

        headers, footers, body = [], [], []

        for b in blocks:
            block_text = b[4].strip()
            y0, y1 = b[1], b[3]
            if block_text:
                if y0 < MAX_HEADER_FOOTER_Y:
                    headers.append(block_text)
                elif y1 > page_height - MAX_HEADER_FOOTER_Y:
                    footers.append(block_text)
                else:
                    body.append(block_text)

        extracted_pages.append({
            "headers": headers,
            "body": body,
            "footers": footers
        })

        # Extract and save unique images
        for idx, img in enumerate(images):
            xref = img[0]
            if xref not in unique_images:
                try:
                    base_img = doc.extract_image(xref)
                    ext = base_img["ext"]
                    img_data = base_img["image"]
                    filename = f"page_{i + 1}_img{idx + 1}.{ext}"
                    path = os.path.join(image_save_dir, filename)
                    with open(path, "wb") as f:
                        f.write(img_data)
                    unique_images[xref] = path
                except Exception as e:
                    st.error(f"Error extracting image on page {i + 1}: {e}")

        # Per-page UI
        st.markdown(f"---\n### 📄 Page {i + 1}")

        with st.expander("📑 Page Metadata"):
            st.json({
                "Page Number": i + 1,
                "Size": f"{page.rect.width} x {page.rect.height}",
                "Rotation": page.rotation,
                "Text Length": len(text),
                "Links": len(links),
                "Images": len(images)
            })

        with st.expander("📝 Extracted Text"):
            st.text(text if text.strip() else "No text found.")

        with st.expander("🔗 Page Links"):
            if links:
                for link in links:
                    st.json(link)
            else:
                st.caption("No links found.")

        with st.expander("🧾 Headers & Footers"):
            st.markdown("**Headers:**" if headers else "No headers found.")
            for h in headers:
                st.markdown(f"- {h}")
            st.markdown("**Footers:**" if footers else "No footers found.")
            for f in footers:
                st.markdown(f"- {f}")

    # -------------------------- TOC SECTION --------------------------
    st.markdown("---")
    st.subheader("📘 Table of Contents (Auto-detected from first pages)")

    toc_raw_text = extract_toc_text(doc)
    toc_entries = parse_toc_lines(toc_raw_text)

    if toc_entries:
        df = pd.DataFrame(toc_entries)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download TOC as CSV", data=csv, file_name="toc.csv", mime="text/csv")
    else:
        st.warning("No structured TOC entries found. Try uploading a TOC-heavy PDF.")

    # -------------------------- IMAGE ZIP DOWNLOAD --------------------------
    st.markdown("---")
    st.header("🖼 Download All Extracted Images")

    if unique_images:
        zip_path = os.path.join(image_save_dir, "all_images.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for path in unique_images.values():
                zipf.write(path, arcname=os.path.basename(path))
        with open(zip_path, "rb") as f:
            st.download_button("📥 Download ZIP", data=f, file_name="all_images.zip", mime="application/zip")
    else:
        st.info("No embedded images found.")

    # -------------------------- PDF RECONSTRUCTION --------------------------
    st.markdown("---")
    st.header("🛠 Reconstruct PDF from Headers, Body, and Footers")

    rebuilt_pdf = os.path.join(image_save_dir, "reconstructed.pdf")
    styles = getSampleStyleSheet()
    output = SimpleDocTemplate(rebuilt_pdf, pagesize=A4)
    elements = []

    for i, p in enumerate(extracted_pages):
        if p["headers"]:
            elements.append(Paragraph("<b>Header:</b>", styles["Heading4"]))
            for h in p["headers"]:
                elements.append(Paragraph(h, styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))

        if p["body"]:
            elements.append(Paragraph("<b>Body:</b>", styles["Heading4"]))
            for line in p["body"]:
                elements.append(Paragraph(line, styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))

        if p["footers"]:
            elements.append(Paragraph("<b>Footer:</b>", styles["Heading4"]))
            for f in p["footers"]:
                elements.append(Paragraph(f, styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))

        elements.append(PageBreak())

    output.build(elements)

    with open(rebuilt_pdf, "rb") as f:
        st.download_button("📄 Download Reconstructed PDF", data=f, file_name="reconstructed.pdf", mime="application/pdf")

else:
    st.info("📤 Please upload a PDF to begin.")


