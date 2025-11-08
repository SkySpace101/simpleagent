"""
SimpleAgent - Core Agent Logic
Processes queries and determines whether to generate code or text output
"""

import os
import re
from typing import Dict, Any, Optional
from app.config import settings


class SimpleAgent:
    """
    Main agent class that processes queries and generates appropriate outputs
    """
    
    def __init__(self):
        """Initialize the agent with configuration"""
        self.openai_api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
        self.model = settings.DEFAULT_MODEL
        self.temperature = settings.DEFAULT_TEMPERATURE

        print(self.google_api_key)
        
        # Determine which API to use (priority: OpenAI > Anthropic > Google)
        self.use_openai = bool(self.openai_api_key)
        self.use_anthropic = bool(self.anthropic_api_key) and not self.use_openai
        self.use_gemini = bool(self.google_api_key) and not self.use_openai and not self.use_anthropic
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process the user query and determine the appropriate response type
        
        Returns:
            Dict with 'type' ('codebase' or 'text'), 'content', and 'metadata'
        """
        # Analyze query to determine if code generation is appropriate
        analysis = await self._analyze_query(query)
        
        if analysis["should_generate_code"] and settings.ENABLE_CODE_GENERATION:
            # Generate codebase
            codebase = await self._generate_codebase(query, analysis)
            return {
                "type": "codebase",
                "content": codebase,
                "metadata": {
                    "language": analysis.get("language", "python"),
                    "framework": analysis.get("framework"),
                    "structure": codebase.get("structure", {})
                }
            }
        else:
            # Generate text response
            text_response = await self._generate_text_response(query, analysis)
            return {
                "type": "text",
                "content": text_response,
                "metadata": {
                    "reason": analysis.get("reason", "Query not suitable for code generation")
                }
            }
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query to determine if code generation is appropriate
        """
        # Keywords that suggest code generation
        code_keywords = [
            "create", "build", "develop", "implement", "write code",
            "application", "app", "program", "script", "function",
            "api", "service", "website", "web app", "database",
            "class", "module", "package", "framework"
        ]
        
        # Keywords that suggest text response
        text_keywords = [
            "explain", "what is", "how does", "describe", "tell me about",
            "information", "definition", "concept", "theory"
        ]
        
        query_lower = query.lower()
        code_score = sum(1 for keyword in code_keywords if keyword in query_lower)
        text_score = sum(1 for keyword in text_keywords if keyword in query_lower)
        
        should_generate_code = code_score > text_score and code_score > 0
        
        # Detect programming language
        language = self._detect_language(query)
        
        # Detect framework
        framework = self._detect_framework(query)
        
        return {
            "should_generate_code": should_generate_code,
            "code_score": code_score,
            "text_score": text_score,
            "language": language,
            "framework": framework,
            "reason": "Code generation suitable" if should_generate_code else "Query better suited for text response"
        }
    
    def _detect_language(self, query: str) -> str:
        """Detect programming language from query"""
        query_lower = query.lower()
        language_keywords = {
            "python": ["python", "py", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node", "react", "vue", "angular"],
            "typescript": ["typescript", "ts"],
            "java": ["java", "spring", "maven"],
            "go": ["go", "golang"],
            "rust": ["rust"],
            "cpp": ["c++", "cpp"],
            "c": ["c programming", "c language"]
        }
        
        for lang, keywords in language_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return lang
        
        return "python"  # Default
    
    def _detect_framework(self, query: str) -> Optional[str]:
        """Detect framework from query"""
        query_lower = query.lower()
        frameworks = {
            "django": "django",
            "flask": "flask",
            "fastapi": "fastapi",
            "react": "react",
            "vue": "vue",
            "angular": "angular",
            "express": "express",
            "spring": "spring"
        }
        
        for keyword, framework in frameworks.items():
            if keyword in query_lower:
                return framework
        
        return None
    
    async def _generate_codebase(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a codebase structure based on the query
        """
        if self.use_openai:
            result = await self._generate_with_openai(query, analysis, codebase=True)
            # Check if we got empty files or fallback code
            if not result.get("files") or self._is_fallback_code(result):
                print("Warning: Received empty or fallback code, generating enhanced code based on query...")
                return await self._generate_enhanced_fallback(query, analysis, result)
            return result
        elif self.use_anthropic:
            result = await self._generate_with_anthropic(query, analysis, codebase=True)
            # Check if we got empty files or fallback code
            if not result.get("files") or self._is_fallback_code(result):
                print("Warning: Received empty or fallback code, generating enhanced code based on query...")
                return await self._generate_enhanced_fallback(query, analysis, result)
            return result
        elif self.use_gemini:
            result = await self._generate_with_gemini(query, analysis, codebase=True)
            # Check if we got empty files or fallback code
            print("I am  here")
            if not result.get("files") or self._is_fallback_code(result):
                print("Warning: Received empty or fallback code, generating enhanced code based on query...")
                return await self._generate_enhanced_fallback(query, analysis, result)
            return result
        else:
            # No API keys - generate enhanced fallback
            print("Warning: No API keys configured. Generating enhanced fallback code based on query.")
            return await self._generate_enhanced_fallback(query, analysis, None)
    
    async def _generate_text_response(self, query: str, analysis: Dict[str, Any]) -> str:
        """
        Generate a text response for queries not suitable for code generation
        """
        if self.use_openai:
            result = await self._generate_with_openai(query, analysis, codebase=False)
            return result.get("content", "Unable to generate response.")
        elif self.use_anthropic:
            result = await self._generate_with_anthropic(query, analysis, codebase=False)
            return result.get("content", "Unable to generate response.")
        elif self.use_gemini:
            result = await self._generate_with_gemini(query, analysis, codebase=False)
            return result.get("content", "Unable to generate response.")
        else:
            return f"Response to query: {query}\n\nThis query is better suited for an informational response rather than code generation."
    
    async def _generate_with_openai(self, query: str, analysis: Dict[str, Any], codebase: bool) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            if codebase:
                prompt = self._build_codebase_prompt(query, analysis)
            else:
                prompt = self._build_text_prompt(query)
            
            # Use lower temperature for code generation to be more deterministic
            temp = 0.3 if codebase else self.temperature
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(codebase)},
                    {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=8000  # Allow for longer code responses
            )
            
            content = response.choices[0].message.content
            
            # Log response for debugging (first 500 chars)
            print(f"OpenAI response preview: {content[:500]}...")
            
            if codebase:
                parsed = self._parse_codebase_response(content, analysis)
                print(f"Parsed {len(parsed.get('files', {}))} files from response")
                return parsed
            else:
                return {"content": content}
        
        except Exception as e:
            print(f"OpenAI API error: {e}")
            print(f"Error details: {type(e).__name__}")
            if codebase:
                print("Falling back to enhanced code generation based on query...")
                return await self._generate_enhanced_fallback(query, analysis, None)
            else:
                return {"content": f"Error generating response: {str(e)}"}
    
    async def _generate_with_anthropic(self, query: str, analysis: Dict[str, Any], codebase: bool) -> Dict[str, Any]:
        """Generate response using Anthropic API"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.anthropic_api_key)
            
            if codebase:
                prompt = self._build_codebase_prompt(query, analysis)
            else:
                prompt = self._build_text_prompt(query)
            
            # Use lower temperature for code generation
            temp = 0.3 if codebase else 0.7
            
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=8000,  # Allow for longer code responses
                temperature=temp,
                messages=[
                    {"role": "user", "content": f"{self._get_system_prompt(codebase)}\n\n{prompt}"}
                ]
            )
            
            content = message.content[0].text
            
            # Log response for debugging (first 500 chars)
            print(f"Anthropic response preview: {content[:500]}...")
            
            if codebase:
                parsed = self._parse_codebase_response(content, analysis)
                print(f"Parsed {len(parsed.get('files', {}))} files from response")
                return parsed
            else:
                return {"content": content}
        
        except Exception as e:
            print(f"Anthropic API error: {e}")
            print(f"Error details: {type(e).__name__}")
            if codebase:
                print("Falling back to enhanced code generation based on query...")
                return await self._generate_enhanced_fallback(query, analysis, None)
            else:
                return {"content": f"Error generating response: {str(e)}"}
    
    async def _generate_with_gemini(self, query: str, analysis: Dict[str, Any], codebase: bool) -> Dict[str, Any]:
        """Generate response using Google Gemini API"""
        print("I am  here 2")
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.google_api_key)
            
            # Use gemini-2.5-flash-lite for all operations
            model_name = "gemini-2.5-flash-lite"
            try:
                model = genai.GenerativeModel(model_name)
            except:
                # Fallback to gemini-2.0-flash-lite if 2.5 is not available
                try:
                    model = genai.GenerativeModel("gemini-2.0-flash-lite")
                except:
                    # Final fallback to gemini-1.5-flash-lite
                    model = genai.GenerativeModel("gemini-1.5-flash-lite")
            
            if codebase:
                prompt = self._build_codebase_prompt(query, analysis)
            else:
                prompt = self._build_text_prompt(query)
            
            # Build the full prompt with system message
            full_prompt = f"{self._get_system_prompt(codebase)}\n\n{prompt}"
            
            # Configure generation parameters
            generation_config = {
                "temperature": 0.3 if codebase else self.temperature,
                "max_output_tokens": 16384,  # Increased for more complete code responses
            }
            
            # Generate response
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Extract text content from response
            if hasattr(response, 'text'):
                content = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                content = response.candidates[0].content.parts[0].text
            else:
                raise ValueError("Unable to extract text from Gemini response")
            
            # Log response for debugging (first 500 chars)
            print(f"Gemini response preview: {content[:500]}...")
            
            if codebase:
                parsed = self._parse_codebase_response(content, analysis)
                print(f"Parsed {len(parsed.get('files', {}))} files from response")
                return parsed
            else:
                return {"content": content}
        
        except Exception as e:
            print(f"Gemini API error: {e}")
            print(f"Error details: {type(e).__name__}")
            if codebase:
                print("Falling back to enhanced code generation based on query...")
                return await self._generate_enhanced_fallback(query, analysis, None)
            else:
                return {"content": f"Error generating response: {str(e)}"}
    
    def _get_system_prompt(self, codebase: bool) -> str:
        """Get system prompt based on output type"""
        if codebase:
            return """You are an expert software developer. Your task is to generate COMPLETE, PRODUCTION-READY code that EXACTLY matches what the user requested.

CRITICAL REQUIREMENTS - CODE COMPLETENESS:
1. Read the user's query CAREFULLY and understand EVERY requirement
2. Generate code that implements EXACTLY what was asked - nothing more, nothing less
3. If the user asks for specific features, include ALL of them
4. If the user specifies a technology/framework, use that EXACT technology
5. The code MUST be COMPLETE and FUNCTIONAL - it should run without errors
6. NO placeholders, NO TODOs, NO incomplete functions
7. Include ALL necessary imports and dependencies
8. Add proper error handling and validation
9. Include example usage or main entry point if applicable
10. Follow the user's specifications precisely

CODE QUALITY REQUIREMENTS:
- Write FULL, COMPLETE implementations - not stubs or skeletons
- Include all necessary imports at the top of each file
- Add proper error handling where appropriate
- Include clear comments explaining complex logic
- Use proper code structure and organization
- Follow language-specific best practices

README REQUIREMENTS (MANDATORY):
You MUST include a comprehensive README.md file with:
1. Clear project description
2. Prerequisites (Python version, Node version, etc.)
3. Step-by-step installation instructions
4. How to install dependencies (pip install, npm install, etc.)
5. How to run the application (exact commands)
6. Usage examples with sample commands
7. Project structure overview
8. Any configuration needed

The README must be detailed enough that someone can clone the project and run it immediately."""
        else:
            return """You are a helpful AI assistant. Provide clear, informative, and well-structured text responses that directly answer the user's query."""
    
    def _build_codebase_prompt(self, query: str, analysis: Dict[str, Any]) -> str:
        """Build prompt for codebase generation"""
        language = analysis.get("language", "python")
        framework = analysis.get("framework")
        
        # Extract specific requirements from query
        requirements = self._extract_requirements(query)
        
        prompt = f"""IMPORTANT: Generate COMPLETE, RUNNABLE code that EXACTLY implements what the user requested. The code must be production-ready and executable.

USER REQUEST:
{query}

SPECIFIC REQUIREMENTS IDENTIFIED:
{requirements}

TECHNICAL SPECIFICATIONS:
- Primary Language: {language}
{f"- Framework: {framework}" if framework else "- Framework: None specified (use standard libraries or most appropriate)"}
- Code Style: Follow {language} best practices

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. Implement EVERY feature mentioned in the user request - make it COMPLETE
2. Use the exact technologies/frameworks specified (if any)
3. The code MUST be FULLY FUNCTIONAL - include all necessary logic, not just stubs
4. Include ALL necessary imports and dependencies - nothing should be missing
5. Add proper error handling, input validation, and edge case handling
6. Include clear comments explaining key functionality and complex logic
7. If it's an application, include a main entry point that can be run directly
8. Make sure all functions are fully implemented - no "pass" statements or empty bodies
9. Include example data or sample usage if applicable

MANDATORY README.md REQUIREMENTS:
You MUST create a comprehensive README.md that includes:
1. **Project Title and Description**: Clear description of what the project does
2. **Prerequisites**: 
   - Required software versions (Python 3.x, Node.js version, etc.)
   - System requirements
3. **Installation Steps** (step-by-step):
   - How to clone/download the project
   - How to set up virtual environment (if applicable)
   - Exact command to install dependencies (e.g., "pip install -r requirements.txt")
4. **How to Run** (exact commands):
   - Command to start/run the application
   - Example: "python main.py" or "npm start" or "uvicorn app:app --reload"
   - Any environment variables needed
5. **Usage Examples**:
   - How to use the application
   - Sample commands or API calls
   - Expected output examples
6. **Project Structure**: Brief overview of important files
7. **Configuration**: Any setup or configuration needed

OUTPUT FORMAT:
Provide the complete codebase using this exact format:
```
FILE: path/to/file.ext
[COMPLETE code content - FULL implementation, NO placeholders, NO TODOs, NO incomplete code]

FILE: another/path/file.ext
[COMPLETE code content - FULL implementation]
```

REQUIRED FILES (ALL must be complete):
- Main application files with FULL implementations
- Configuration files (if needed) with actual values
- Dependencies file (requirements.txt for Python, package.json for Node.js, etc.) with ALL required packages
- README.md with COMPREHENSIVE setup and run instructions (this is MANDATORY)

CODE COMPLETENESS CHECKLIST:
✓ All functions have complete implementations
✓ All imports are included
✓ All dependencies are listed
✓ Main entry point exists and works
✓ Error handling is in place
✓ README has clear run instructions
✓ Code can be executed immediately after setup

Remember: Generate COMPLETE, PRODUCTION-READY code. Someone should be able to install dependencies and run the code immediately without any modifications."""
        
        return prompt
    
    def _extract_requirements(self, query: str) -> str:
        """Extract specific requirements from the query to help the LLM understand better"""
        requirements = []
        query_lower = query.lower()
        
        # Detect specific features
        if "authentication" in query_lower or "login" in query_lower or "auth" in query_lower:
            requirements.append("- User authentication/login functionality")
        if "database" in query_lower or "db" in query_lower or "sql" in query_lower:
            requirements.append("- Database integration")
        if "api" in query_lower or "rest" in query_lower or "endpoint" in query_lower:
            requirements.append("- API endpoints/REST API")
        if "crud" in query_lower or "create" in query_lower or "read" in query_lower or "update" in query_lower or "delete" in query_lower:
            requirements.append("- CRUD operations")
        if "todo" in query_lower or "task" in query_lower:
            requirements.append("- Todo/task management features")
        if "web" in query_lower or "website" in query_lower or "html" in query_lower:
            requirements.append("- Web interface/HTML pages")
        if "visualization" in query_lower or "chart" in query_lower or "graph" in query_lower or "plot" in query_lower:
            requirements.append("- Data visualization/charts")
        if "csv" in query_lower or "excel" in query_lower or "data" in query_lower:
            requirements.append("- Data file processing")
        if "cli" in query_lower or "command" in query_lower or "terminal" in query_lower:
            requirements.append("- Command-line interface")
        
        if not requirements:
            requirements.append("- Implement the functionality described in the user's request")
        
        return "\n".join(requirements)
    
    def _build_text_prompt(self, query: str) -> str:
        """Build prompt for text response"""
        return f"""Please provide a comprehensive, well-structured response to the following query:

{query}

Make sure your response is:
- Clear and informative
- Well-organized with proper sections
- Easy to understand
- Comprehensive but concise"""
    
    def _parse_codebase_response(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured codebase format"""
        files = {}
        current_file = None
        current_content = []
        in_code_block = False
        code_block_lang = None
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for FILE: marker
            if line.strip().startswith('FILE:'):
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                current_file = line.replace('FILE:', '').strip()
                current_content = []
                in_code_block = False
            # Check for code block markers
            elif line.strip().startswith('```'):
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    code_block_lang = line.strip()[3:].strip()
                    # If we have a current file, this might be code for it
                    if current_file and not current_content:
                        # This is the start of code for current file
                        pass
                    elif not current_file:
                        # Code block without FILE: marker - try to infer filename
                        if code_block_lang:
                            ext_map = {
                                'python': 'py', 'py': 'py',
                                'javascript': 'js', 'js': 'js',
                                'typescript': 'ts', 'ts': 'ts',
                                'html': 'html', 'css': 'css',
                                'json': 'json', 'yaml': 'yml', 'yml': 'yml',
                                'markdown': 'md', 'md': 'md'
                            }
                            ext = ext_map.get(code_block_lang.lower(), 'txt')
                            if 'main' in code_block_lang.lower() or not current_file:
                                current_file = f"main.{ext}"
                            else:
                                current_file = f"file.{ext}"
                else:
                    # Ending a code block
                    in_code_block = False
                    if current_file:
                        # Save current file if we have one
                        if current_content:
                            files[current_file] = '\n'.join(current_content).strip()
                        current_file = None
                        current_content = []
            elif current_file:
                # We're inside a file, add line to content
                current_content.append(line)
            elif line.strip() and not line.startswith('```') and not in_code_block:
                # Content that might be README or documentation
                if not any(f.startswith('README') or f.endswith('.md') for f in files.keys()):
                    if 'README.md' not in files:
                        files['README.md'] = line
                    else:
                        files['README.md'] += '\n' + line
            
            i += 1
        
        # Save last file if exists
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content).strip()
        
        # If no files were parsed, try alternative parsing
        if not files:
            print("No files found with FILE: markers, trying alternative parsing...")
            files = self._parse_alternative_format(content, analysis)
        
        # If still no files, log and create enhanced fallback
        if not files:
            print("Warning: Could not parse any files from LLM response. Content preview:")
            print(content[:1000])
            print("Generating enhanced fallback based on query...")
            # Don't use basic structure, use enhanced fallback
            return {
                "files": {},  # Will trigger enhanced fallback
                "structure": {}
            }
        
        # Ensure README.md exists - if not, generate a comprehensive one
        readme_exists = any(
            f.lower().endswith('readme.md') or f.lower() == 'readme.md' 
            for f in files.keys()
        )
        
        if not readme_exists:
            print("Warning: README.md not found in generated files. Creating comprehensive README...")
            language = analysis.get("language", "python")
            framework = analysis.get("framework")
            requirements = self._extract_requirements("")  # We'll use the query from context
            
            # Generate a comprehensive README
            readme_content = self._generate_comprehensive_readme(
                files, language, framework, analysis
            )
            files["README.md"] = readme_content
        
        return {
            "files": files,
            "structure": self._build_structure_tree(files)
        }
    
    def _parse_alternative_format(self, content: str, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Try to parse code in alternative formats (markdown code blocks, etc.)"""
        files = {}
        language = analysis.get("language", "python")
        
        # Look for markdown code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        
        if code_blocks:
            for i, (lang, code) in enumerate(code_blocks):
                lang = lang or language
                ext_map = {
                    'python': 'py', 'py': 'py',
                    'javascript': 'js', 'js': 'js',
                    'typescript': 'ts', 'ts': 'ts',
                    'html': 'html', 'css': 'css',
                    'json': 'json'
                }
                ext = ext_map.get(lang.lower(), 'txt')
                filename = f"main.{ext}" if i == 0 else f"file_{i}.{ext}"
                files[filename] = code.strip()
        
        # Extract README from text before/after code blocks
        text_parts = re.split(r'```.*?```', content, flags=re.DOTALL)
        readme_text = '\n\n'.join([p.strip() for p in text_parts if p.strip() and not p.strip().startswith('FILE:')])
        if readme_text and len(readme_text) > 50:  # Only add if substantial
            files['README.md'] = readme_text
        
        return files
    
    def _create_basic_structure(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create a basic code structure when parsing fails"""
        language = analysis.get("language", "python")
        
        if language == "python":
            return {
                "main.py": "# Main application file\nprint('Hello, World!')",
                "requirements.txt": "# Project dependencies",
                "README.md": "# Project README\n\nThis project was generated by SimpleAgent."
            }
        elif language in ["javascript", "typescript"]:
            return {
                "index.js": "// Main application file\nconsole.log('Hello, World!');",
                "package.json": '{\n  "name": "project",\n  "version": "1.0.0"\n}',
                "README.md": "# Project README\n\nThis project was generated by SimpleAgent."
            }
        else:
            return {
                "main." + language: f"// Main application file\n// Generated by SimpleAgent",
                "README.md": "# Project README\n\nThis project was generated by SimpleAgent."
            }
    
    def _build_structure_tree(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Build a tree structure of the codebase"""
        structure = {}
        for file_path in files.keys():
            parts = file_path.split('/')
            current = structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = "file"
        return structure
    
    def _is_fallback_code(self, result: Dict[str, Any]) -> bool:
        """Check if the result contains only fallback/placeholder code"""
        files = result.get("files", {})
        if not files:
            return True
        
        # Check for common fallback patterns
        fallback_patterns = [
            "Hello, World",
            "TODO: Implement",
            "basic template",
            "placeholder",
            "print('Hello"
        ]
        
        for file_path, content in files.items():
            content_lower = content.lower()
            # If we find actual implementation code, it's not fallback
            if any(pattern.lower() in content_lower for pattern in fallback_patterns):
                # But check if there's also real code
                if len(content) > 200:  # Substantial code
                    return False
                # Check for function definitions, classes, etc.
                if any(keyword in content for keyword in ["def ", "class ", "function ", "const ", "let ", "var "]):
                    if len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('//')]) > 5:
                        return False
        
        # If all files are very short or contain only fallback patterns, it's fallback
        total_code_lines = sum(len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')]) for content in files.values())
        return total_code_lines < 10
    
    async def _generate_enhanced_fallback(self, query: str, analysis: Dict[str, Any], existing_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an enhanced fallback codebase that actually implements query requirements"""
        language = analysis.get("language", "python")
        framework = analysis.get("framework")
        requirements = self._extract_requirements(query)
        
        # Generate code based on detected requirements
        files = {}
        
        if language == "python":
            # Generate main.py based on requirements
            main_code = self._generate_python_code(query, requirements, framework)
            files["main.py"] = main_code
            
            # Generate requirements.txt based on detected needs
            deps = self._generate_dependencies(requirements, language, framework)
            files["requirements.txt"] = deps
            
        elif language in ["javascript", "typescript"]:
            ext = "ts" if language == "typescript" else "js"
            main_code = self._generate_js_code(query, requirements, framework, ext)
            files[f"main.{ext}"] = main_code
            
            # Generate package.json
            package_json = self._generate_package_json(requirements, framework)
            files["package.json"] = package_json
        else:
            # Generic fallback
            files[f"main.{language}"] = f"// Generated by SimpleAgent\n// Query: {query}\n// Implement the requested functionality here"
        
        # Generate comprehensive README
        readme = self._generate_readme(query, requirements, language, framework)
        files["README.md"] = readme
        
        return {
            "files": files,
            "structure": self._build_structure_tree(files)
        }
    
    def _generate_python_code(self, query: str, requirements: str, framework: Optional[str]) -> str:
        """Generate Python code based on query requirements"""
        code_parts = [f'"""\nGenerated by SimpleAgent\nQuery: {query}\n"""\n']
        
        # Add imports based on requirements
        imports = []
        if "api" in query.lower() or "rest" in query.lower():
            if framework == "fastapi":
                imports.append("from fastapi import FastAPI, HTTPException")
                imports.append("from pydantic import BaseModel")
            elif framework == "flask":
                imports.append("from flask import Flask, request, jsonify")
            else:
                imports.append("from http.server import HTTPServer, BaseHTTPRequestHandler")
                imports.append("import json")
        
        if "database" in query.lower() or "db" in query.lower() or "sql" in query.lower():
            imports.append("import sqlite3")
            imports.append("import os")
        
        if "csv" in query.lower() or "data" in query.lower():
            imports.append("import csv")
            imports.append("import pandas as pd")
        
        if "authentication" in query.lower() or "login" in query.lower() or "auth" in query.lower():
            imports.append("import hashlib")
            imports.append("import secrets")
        
        if "todo" in query.lower() or "task" in query.lower():
            imports.append("from datetime import datetime")
            imports.append("from typing import List, Dict, Optional")
        
        if imports:
            code_parts.append("\n".join(imports))
            code_parts.append("")
        
        # Generate main functionality
        if framework == "fastapi":
            code_parts.append("app = FastAPI(title=\"Generated Application\")\n")
            code_parts.append("@app.get(\"/\")\ndef read_root():\n    return {\"message\": \"Application is running\"}\n")
            code_parts.append("@app.get(\"/health\")\ndef health_check():\n    return {\"status\": \"healthy\"}\n")
        elif framework == "flask":
            code_parts.append("app = Flask(__name__)\n")
            code_parts.append("@app.route('/')\ndef index():\n    return jsonify({\"message\": \"Application is running\"})\n")
        else:
            # Standard Python script
            code_parts.append("def main():")
            code_parts.append('    """Main function implementing the requested functionality"""')
            
            if "todo" in query.lower() or "task" in query.lower():
                code_parts.append("    # Todo list functionality")
                code_parts.append("    todos = []")
                code_parts.append("    print(\"Todo list application initialized\")")
            elif "api" in query.lower():
                code_parts.append("    # API functionality")
                code_parts.append("    print(\"API server would start here\")")
            elif "database" in query.lower():
                code_parts.append("    # Database functionality")
                code_parts.append("    print(\"Database operations would be performed here\")")
            else:
                code_parts.append(f"    # Implement: {query[:100]}")
                code_parts.append("    print(\"Application started\")")
            
            code_parts.append("")
            code_parts.append('if __name__ == "__main__":')
            code_parts.append("    main()")
        
        return "\n".join(code_parts)
    
    def _generate_js_code(self, query: str, requirements: str, framework: Optional[str], ext: str) -> str:
        """Generate JavaScript/TypeScript code based on query requirements"""
        code_parts = []
        
        if ext == "ts":
            code_parts.append("// Generated by SimpleAgent")
            code_parts.append(f"// Query: {query}\n")
            code_parts.append("interface Config {")
            code_parts.append("  // Add configuration interface here")
            code_parts.append("}\n")
        else:
            code_parts.append("// Generated by SimpleAgent")
            code_parts.append(f"// Query: {query}\n")
        
        if framework == "react":
            code_parts.append("import React from 'react';\n")
            code_parts.append("function App() {")
            code_parts.append("  return (")
            code_parts.append("    <div className=\"App\">")
            code_parts.append("      <h1>Generated Application</h1>")
            code_parts.append("    </div>")
            code_parts.append("  );")
            code_parts.append("}\n")
            code_parts.append("export default App;")
        elif framework == "express" or "api" in query.lower():
            code_parts.append("const express = require('express');")
            code_parts.append("const app = express();\n")
            code_parts.append("app.use(express.json());\n")
            code_parts.append("app.get('/', (req, res) => {")
            code_parts.append("  res.json({ message: 'Application is running' });")
            code_parts.append("});\n")
            code_parts.append("const PORT = process.env.PORT || 3000;")
            code_parts.append("app.listen(PORT, () => {")
            code_parts.append("  console.log(`Server running on port ${PORT}`);")
            code_parts.append("});")
        else:
            code_parts.append("// Main application code")
            code_parts.append("function main() {")
            code_parts.append(f"  // Implement: {query[:80]}")
            code_parts.append("  console.log('Application started');")
            code_parts.append("}\n")
            code_parts.append("main();")
        
        return "\n".join(code_parts)
    
    def _generate_dependencies(self, requirements: str, language: str, framework: Optional[str]) -> str:
        """Generate dependencies file based on requirements"""
        deps = []
        
        if language == "python":
            if framework == "fastapi":
                deps.append("fastapi==0.104.1")
                deps.append("uvicorn[standard]==0.24.0")
            elif framework == "flask":
                deps.append("flask==3.0.0")
            
            if "database" in requirements.lower() or "sql" in requirements.lower():
                deps.append("sqlalchemy==2.0.23")
            
            if "csv" in requirements.lower() or "data" in requirements.lower():
                deps.append("pandas==2.1.3")
            
            if not deps:
                deps.append("# Add your dependencies here")
        
        return "\n".join(deps) if deps else "# No specific dependencies identified"
    
    def _generate_package_json(self, requirements: str, framework: Optional[str]) -> str:
        """Generate package.json for Node.js projects"""
        deps = {}
        
        if framework == "express" or "api" in requirements.lower():
            deps["express"] = "^4.18.2"
        
        if framework == "react":
            deps["react"] = "^18.2.0"
            deps["react-dom"] = "^18.2.0"
        
        deps_str = ",\n    ".join([f'"{k}": "{v}"' for k, v in deps.items()])
        
        return f"""{{
  "name": "generated-project",
  "version": "1.0.0",
  "description": "Generated by SimpleAgent",
  "main": "main.js",
  "scripts": {{
    "start": "node main.js"
  }},
  "dependencies": {{
    {deps_str if deps_str else '// Add dependencies here'}
  }}
}}"""
    
    def _generate_comprehensive_readme(self, files: Dict[str, str], language: str, framework: Optional[str], analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive README based on generated files"""
        # Detect main entry point
        main_file = None
        for filename in files.keys():
            if filename.endswith('main.py') or filename.endswith('main.js') or filename.endswith('main.ts') or filename == 'app.py' or filename == 'index.js':
                main_file = filename
                break
        
        if not main_file:
            # Try to find any Python/JS file
            for filename in files.keys():
                if filename.endswith('.py') or filename.endswith('.js') or filename.endswith('.ts'):
                    main_file = filename
                    break
        
        # Detect if it's a web app
        is_web_app = any('app' in f.lower() or 'server' in f.lower() or 'api' in f.lower() 
                         for f in files.keys()) or framework in ['fastapi', 'flask', 'express', 'react']
        
        # Detect dependencies file
        has_requirements = 'requirements.txt' in files
        has_package_json = 'package.json' in files
        
        readme = f"""# Generated Project

## Description
This project was generated by SimpleAgent. Please review the code and customize as needed.

## Technology Stack
- Language: {language}
{f"- Framework: {framework}" if framework else ""}

## Prerequisites
"""
        
        if language == "python":
            readme += """- Python 3.8 or higher
- pip (Python package manager)
"""
            if framework:
                readme += f"- {framework} framework\n"
        elif language in ["javascript", "typescript"]:
            readme += """- Node.js 14.x or higher
- npm (Node Package Manager)
"""
            if framework:
                readme += f"- {framework} framework\n"
        
        readme += "\n## Installation\n\n"
        
        if language == "python":
            readme += """1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\\Scripts\\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
"""
        elif language in ["javascript", "typescript"]:
            readme += """1. Install dependencies:
   ```bash
   npm install
   ```
"""
        
        readme += "\n## How to Run\n\n"
        
        if is_web_app:
            if framework == "fastapi":
                readme += """Run the FastAPI application:
   ```bash
   uvicorn main:app --reload
   ```
   
   Or if using app.py:
   ```bash
   uvicorn app:app --reload
   ```
   
   The application will be available at: http://localhost:8000
"""
            elif framework == "flask":
                readme += f"""Run the Flask application:
   ```bash
   python {main_file or 'app.py'}
   ```
   
   The application will be available at: http://localhost:5000
"""
            elif framework == "express":
                readme += """Run the Express server:
   ```bash
   npm start
   ```
   
   Or:
   ```bash
   node main.js
   ```
   
   The server will be available at: http://localhost:3000
"""
            else:
                if main_file:
                    if language == "python":
                        readme += f"""Run the application:
   ```bash
   python {main_file}
   ```
"""
                    else:
                        readme += f"""Run the application:
   ```bash
   node {main_file}
   ```
"""
        else:
            if main_file:
                if language == "python":
                    readme += f"""Run the script:
   ```bash
   python {main_file}
   ```
"""
                else:
                    readme += f"""Run the script:
   ```bash
   node {main_file}
   ```
"""
            else:
                readme += f"""Run the main file:
   ```bash
   python main.py
   ```
   (Adjust the command based on your main entry point)
"""
        
        readme += "\n## Project Structure\n\n"
        readme += "Key files in this project:\n\n"
        for filename in sorted(files.keys())[:10]:  # Show first 10 files
            readme += f"- `{filename}`\n"
        
        readme += "\n## Usage\n\n"
        readme += "Please refer to the code comments and implementation for usage details.\n"
        
        readme += "\n## Notes\n\n"
        readme += "- This code was automatically generated. Please review and test before production use.\n"
        readme += "- Make sure all dependencies are installed before running.\n"
        if not has_requirements and not has_package_json:
            readme += "- **Important**: Dependencies file may be missing. Please check and add required packages.\n"
        
        return readme
    
    def _generate_readme(self, query: str, requirements: str, language: str, framework: Optional[str]) -> str:
        """Generate comprehensive README"""
        readme = f"""# Generated Project

## Description
This project was generated by SimpleAgent based on the following request:

{query}

## Requirements Identified
{requirements}

## Technology Stack
- Language: {language}
{f"- Framework: {framework}" if framework else ""}

## Setup Instructions

### Prerequisites
- {language.capitalize()} installed
{f"- {framework} framework" if framework else ""}

### Installation
"""
        
        if language == "python":
            readme += """1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```
"""
        elif language in ["javascript", "typescript"]:
            readme += """1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the application:
   ```bash
   npm start
   # or
   node main.js
   ```
"""
        
        readme += f"""
## Implementation Notes
This code was generated based on your query. Please review and customize as needed to fully implement all requirements.

## Next Steps
1. Review the generated code
2. Implement any missing functionality
3. Add tests
4. Customize based on your specific needs
"""
        
        return readme

