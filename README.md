# 📄 PDF Extractor – Metadata, Text, Links, TOC, Headers, Images

A powerful Streamlit web app that extracts, analyzes, and reconstructs PDF content using [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/), OpenCV, and ReportLab. The app identifies headers, footers, body content, images, metadata, hyperlinks, and Table of Contents entries.

---

## 🚀 Features

✅ Upload and parse any PDF file  
✅ Extract:
- Text, metadata, embedded images
- Headers, footers, and main body text (based on Y-coordinate thresholds)
- All hyperlinks per page
✅ Detect Table of Contents using regex-based patterns  
✅ Download all extracted images as a ZIP  
✅ Reconstruct the parsed content into a new PDF using ReportLab  
✅ Fully interactive web interface via Streamlit

---

## 🖼 App Demo (Screenshots)

| Upload PDF | Extracted TOC & Metadata |
|------------|--------------------------|
| ![Upload](https://i.imgur.com/aUxO3Nl.png) | ![TOC](https://i.imgur.com/DzYOQvm.png) |

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| **Streamlit** | Frontend Web Interface |
| **PyMuPDF (fitz)** | PDF Text, Image, and Layout Parsing |
| **ReportLab** | PDF Reconstruction |
| **Regex** | Table of Contents Detection |
| **Pillow (PIL)** | Image Handling |
| **Zipfile** | Download all extracted images |

---


---

## 🧪 How to Run Locally

1. **Clone this repository**
```bash
git clone https://github.com/yourusername/pdf-extractor-app.git
cd pdf-extractor-app

Create virtual environment (optional but recommended)
