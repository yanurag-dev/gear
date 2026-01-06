import os
import pathlib
import mimetypes
import logging
from typing import List, Optional
from src.llm.gemini import get_gemini_multimodal_response

_logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self, knowledge_base_dir: str):
        self.knowledge_base_dir = knowledge_base_dir

    def load_all_documents(self) -> str:
        """
        Recursively scans the knowledge base directory and extracts text from all documents.
        """
        if not os.path.exists(self.knowledge_base_dir):
            _logger.warning(f"Knowledge base directory does not exist: {self.knowledge_base_dir}")
            return ""

        all_content = []
        for root, _, files in os.walk(self.knowledge_base_dir):
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                content = self._load_file(file_path)
                if content:
                    all_content.append(f"--- DOCUMENT: {file} ---\n{content}\n")
        
        return "\n".join(all_content)

    def _load_file(self, file_path: str) -> Optional[str]:
        mime_type, _ = mimetypes.guess_type(file_path)
        ext = pathlib.Path(file_path).suffix.lower()

        try:
            if ext in ['.txt', '.md', '.json']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif ext == '.pdf' or (mime_type and (mime_type.startswith('image/') or mime_type == 'application/pdf')):
                _logger.info(f"Extracting text from multimodal file: {file_path}")
                return get_gemini_multimodal_response(
                    prompt="Extract all text and key information from this document. Maintain the layout structure as much as possible. If it's a resume, extract sections like Experience, Education, Skills, etc.",
                    file_path=file_path
                )
            else:
                _logger.debug(f"Skipping unsupported file type: {file_path}")
                return None
        except Exception as e:
            _logger.error(f"Error loading file {file_path}: {e}")
            return None
