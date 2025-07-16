# 📄 PDF Extractor – Metadata, TOC, Headers, Footers, Text, and Images

A powerful PDF content extraction and reconstruction tool built with **Streamlit**, **PyMuPDF (fitz)**, and **ReportLab**. This application can analyze and restructure PDFs by detecting metadata, headers, footers, body text, links, images, and table of contents entries.

---

## 🚀 Features

✅ Upload any PDF and view page-wise content  
✅ Extract:
- **Headers & Footers** (via coordinate thresholds)
- **Body Text** (main content)
- **Metadata** (page size, rotation, etc.)
- **Hyperlinks**
- **Embedded Images**
✅ Detect **Table of Contents (TOC)** using regex  
✅ Download all images as a ZIP archive  
✅ Generate a reconstructed, readable PDF using **ReportLab**  
✅ Clean UI built with **Streamlit**

---

## 🛠️ Tech Stack

| Tool / Library | Purpose |
|----------------|---------|
| `streamlit` | UI frontend |
| `PyMuPDF (fitz)` | PDF parsing, text block layout, and image extraction |
| `ReportLab` | PDF reconstruction |
| `PIL` / `Pillow` | Image handling |
| `re` | Regex for TOC detection |
| `zipfile` | Image packaging and download |

---

## 🧑‍💻 Local Setup Guide

Follow these steps to run the app on your local machine.

### 1. ✅ Clone the Repository

```bash
git clone https://github.com/your-username/pdf-extractor-app.git
cd pdf-extractor-app

### 2. 📦 Create a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


### 3. 📥 Install Required Packages
```bash
pip install -r requirements.txt

### 4. 🚀 Launch the App
```bash
streamlit run app.py

### 5. 🌐 Open in Browser
Visit http://localhost:8501 to interact with the PDF Extractor.
