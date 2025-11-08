"""
Output management utilities for generating codebases and text files
"""

from pathlib import Path
import zipfile
import shutil
from datetime import datetime
from typing import Dict, Any
import os


class OutputManager:
    """Manages generation of output files (codebase zip or text files)"""
    
    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_output(self, result: Dict[str, Any], original_query: str) -> Path:
        """
        Generate output file based on result type
        
        Args:
            result: Result dictionary from agent with 'type' and 'content'
            original_query: Original user query for naming
            
        Returns:
            Path to generated output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if result["type"] == "codebase":
            return await self._generate_codebase_zip(result, original_query, timestamp)
        else:
            return await self._generate_text_file(result, original_query, timestamp)
    
    async def _generate_codebase_zip(self, result: Dict[str, Any], query: str, timestamp: str) -> Path:
        """Generate a zip file containing the codebase"""
        # Create temporary directory for codebase
        temp_dir = self.output_dir / f"codebase_{timestamp}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            files = result["content"].get("files", {})
            
            # Write all files to temporary directory
            for file_path, content in files.items():
                full_path = temp_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            # Create zip file
            zip_filename = f"codebase_{timestamp}.zip"
            zip_path = self.output_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            return zip_path
        
        except Exception as e:
            # Clean up on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise Exception(f"Error generating codebase: {str(e)}")
    
    async def _generate_text_file(self, result: Dict[str, Any], query: str, timestamp: str) -> Path:
        """Generate a text file with the response"""
        content = result.get("content", "")
        if isinstance(content, dict):
            content = content.get("content", str(content))
        
        # Create formatted text file
        text_content = f"""SimpleAgent Response
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Original Query: {query}

{'=' * 80}

{content}

{'=' * 80}

Metadata: {result.get('metadata', {})}
"""
        
        filename = f"response_{timestamp}.txt"
        file_path = self.output_dir / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        
        return file_path


