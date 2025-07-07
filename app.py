import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import pandas as pd
from collections import Counter
import pdfplumber
import tempfile
import re

st.set_page_config(page_title="PDF Extractor by PyMuPDF", layout="wide")
st.title("📄 PDF Extractor – Metadata, Text, Links, TOC, Tables & Images")

uploaded_file = st.file_uploader("📤 Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.success(f"✅ PDF loaded successfully! Total Pages: {doc.page_count}")

    # Store unique images using their xref as keys
    unique_images = {}
    toc_candidates = []

    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text()
        links = page.get_links()
        embedded_images = page.get_images(full=True)

        # Collect lines for TOC detection
        toc_candidates.extend(page.get_text("text").splitlines())

        # Collect unique embedded images
        for img in embedded_images:
            xref = img[0]
            if xref not in unique_images:
                try:
                    base_image = doc.extract_image(xref)
                    unique_images[xref] = {
                        "page": i + 1,
                        "image": base_image["image"],
                        "ext": base_image["ext"]
                    }
                except Exception as e:
                    st.error(f"⚠️ Error extracting image on page {i + 1}: {e}")

        # ─── Per Page Content ─────────────────────────────
        st.markdown(f"---\n### 📄 Page {i + 1}")

        # 📑 Page Metadata
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

        # 📝 Extracted Text
        with st.expander("📝 Extracted Text"):
            if text.strip():
                st.text(text)
            else:
                st.warning("No text found on this page.")

        # 🔗 Links
        if links:
            with st.expander("🔗 Page Links"):
                for link in links:
                    st.json(link)
        else:
            st.caption("🔗 No links found on this page.")

    # ─── Table of Contents Detection ─────────────────────
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

    # ─── Tables Section (via pdfplumber) ─────────────────────
    st.markdown("---")
    st.subheader("📊 Tables (via pdfplumber)")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_pdf_path = tmp_file.name

        with pdfplumber.open(tmp_pdf_path) as plumber_pdf:
            table_found = False
            for page_num, page in enumerate(plumber_pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for t_index, table in enumerate(tables):
                        df = pd.DataFrame(table)
                        st.write(f"📄 Page {page_num + 1} – Table {t_index + 1}")
                        st.dataframe(df)
                        table_found = True

            if not table_found:
                st.info("ℹ️ No tables detected in the PDF using pdfplumber.")
    except Exception as e:
        st.error(f"❌ Table extraction failed: {e}")

    # ─── Final Section: All Unique Embedded Images ─────────────────────
    st.markdown("---")
    st.header("📸 All Embedded Images in PDF")

    if unique_images:
        for idx, (xref, item) in enumerate(unique_images.items(), start=1):
            image = Image.open(io.BytesIO(item["image"]))
            st.image(
                image,
                caption=f"📷 Image {idx} (first seen on Page {item['page']}, format: {item['ext']})",
                use_container_width=False
            )
    else:
        st.info("No embedded images found in the entire PDF.")

else:
    st.info("📤 Upload a PDF file to begin.")
