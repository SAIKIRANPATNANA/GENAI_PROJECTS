# Blood Report Parsing IISc

AI-assisted blood report parsing project created during IISc Bangalore OpenHack 2025.

## What It Does

- parses heterogeneous blood reports from PDFs and images
- combines OCR, LLM-based extraction, and structured report generation
- supports abnormality detection and health-trend style analysis
- includes web-app style prototypes built across multiple development rounds

## Tech Stack

- Python
- Flask
- Streamlit-style AI workflows
- LangChain
- Gemini
- Groq-hosted LLMs
- Tesseract OCR
- FAISS / structured data workflows
- SQLite

## Security Note

This cleaned version is configured to use environment variables for secrets. Do not commit API keys, SMTP credentials, service-account JSON files, notebooks with outputs, or generated database artifacts.
