\# SMART MATCH ASSISTANT



SMART MATCH ASSISTANT is a secure document matching application built with Flask, MySQL, and Python.



It helps users compare records from different documents and find matching records based on identifiers and other record information.



\## Features



\- User registration and login

\- Secure password hashing

\- User-specific document access

\- Secure document upload

\- File type and content validation

\- Maximum file size protection

\- CSRF protection

\- Security headers

\- Session security

\- Main Document and Secondary Document matching

\- Exact identifier matching

\- Fuzzy matching

\- Duplicate and ambiguous match detection

\- Matched and unmatched results

\- PDF, DOCX, XLSX, and TXT exports

\- OCR support for image documents

\- PDF, Word, Excel, and TXT document processing

\- MySQL database storage



\## Supported Documents



The application supports:



\- PDF

\- DOCX

\- XLSX

\- TXT

\- PNG

\- JPG

\- JPEG



Images can be processed using OCR.



\## Matching Process



The matching process works approximately as follows:



1\. User uploads documents.

2\. The application validates the uploaded files.

3\. Document content is extracted.

4\. OCR is used when required.

5\. Data is normalized.

6\. Important identifiers are detected.

7\. Records are compared.

8\. Exact matching is attempted first.

9\. Fuzzy matching is used when necessary.

10\. Duplicate or ambiguous candidates are identified.

11\. Results are displayed to the user.

12\. Results can be exported.



\## Matching Results



The application provides three main result categories:



\### Matched



Records where a reliable match is found.



\### Unmatched



Records where no suitable matching record is found.



\### Duplicate / Ambiguous



Records where multiple possible matches exist or the system cannot safely choose one.



The application avoids guessing when a match is ambiguous.



\## Technology Stack



\- Python

\- Flask

\- Flask-SQLAlchemy

\- Flask-Login

\- Flask-WTF

\- Flask-Limiter

\- MySQL

\- PyMySQL

\- Pandas

\- OpenPyXL

\- PyMuPDF

\- python-docx

\- Tesseract OCR

\- scikit-learn

\- Sentence Transformers

\- ReportLab

\- pytest



\## Project Structure



```text

first project/

│

├── app/

│   ├── routes/

│   ├── models/

│   ├── services/

│   │   ├── extractors/

│   │   ├── ocr/

│   │   ├── matching/

│   │   ├── normalization/

│   │   └── exporters/

│   ├── templates/

│   ├── static/

│   └── \_\_init\_\_.py

│

├── config/

│   └── config.py

│

├── tests/

│

├── uploads/

├── outputs/

├── venv/

│

├── .env

├── .env.example

├── .gitignore

├── requirements.txt

├── README.md

└── run.py

