"""
File processing utilities for handling uploaded files
"""

from fastapi import UploadFile, HTTPException
from pathlib import Path
import PyPDF2
import io
from typing import Optional


class FileProcessor:
    """Handles processing of uploaded files (PDF, TXT)"""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.supported_extensions = {'.pdf', '.txt', '.md', '.docx'}
    
    async def process_uploaded_file(self, file: UploadFile) -> str:
        """
        Process uploaded file and extract text content
        
        Args:
            file: Uploaded file object
            
        Returns:
            Extracted text content as string
        """
        # Check file size
        content = await file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size / 1024 / 1024}MB"
            )
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: {', '.join(self.supported_extensions)}"
            )
        
        # Extract text based on file type
        if file_extension == '.pdf':
            return self._extract_from_pdf(content)
        elif file_extension == '.txt' or file_extension == '.md':
            return content.decode('utf-8')
        elif file_extension == '.docx':
            return self._extract_from_docx(content)
        else:
            raise HTTPException(status_code=400, detail="Unable to process file type")
    
    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
            
            return '\n'.join(text_content)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error extracting text from PDF: {str(e)}"
            )
    
    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            from docx import Document
            docx_file = io.BytesIO(content)
            doc = Document(docx_file)
            
            text_content = []
            for paragraph in doc.paragraphs:
                text_content.append(paragraph.text)
            
            return '\n'.join(text_content)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error extracting text from DOCX: {str(e)}"
            )


