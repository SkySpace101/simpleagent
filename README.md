# SimpleAgent

An AI-powered agent that processes human queries and generates executable codebases or text responses based on the query's suitability.

## Features

- **Query Processing**: Enter natural language queries to describe what you want to build
- **File Upload Support**: Upload PDF, TXT, or DOCX files with additional context
- **Intelligent Output**: Automatically determines whether to generate code or provide text responses
- **Code Generation**: Creates well-structured, production-ready codebases with proper organization
- **Template System**: Pre-built query templates for common use cases
- **Simple UI**: Clean, minimalist interface with excellent UX

## Project Structure

```
simple_agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agent.py         # Core agent logic
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_processor.py    # File upload processing
│   │   └── output_manager.py    # Output generation
│   └── static/
│       ├── index.html       # Frontend UI
│       ├── style.css        # Styling
│       └── script.js        # Frontend logic
├── outputs/                 # Generated outputs directory
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd simple_agent
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # OR
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   
   **Note**: You need at least one API key (OpenAI, Anthropic, or Google Gemini) for the agent to work. The agent will use APIs in the following priority order: OpenAI > Anthropic > Google Gemini. If no API key is provided, the agent will use a fallback mode with basic code generation.

5. **Run the application:**
   ```bash
   python -m app.main
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application:**
   
   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Usage

### Basic Workflow

1. **Enter a Query**: Type your request in the query textarea. For example:
   - "Create a simple web application with a todo list feature"
   - "Build a REST API with user authentication"
   - "Generate a Python script for data analysis"

2. **Upload Context (Optional)**: Upload a PDF, TXT, or DOCX file with additional requirements or context.

3. **Use Templates (Optional)**: Click "Load Template" to see pre-built query templates and select one.

4. **Submit**: Click "Process Query" to generate the output.

5. **Download**: Once processing is complete, download the generated codebase (ZIP) or text response (TXT).

### Query Examples

**Code Generation Queries:**
- "Create a FastAPI application with user authentication and JWT tokens"
- "Build a React component library with TypeScript"
- "Generate a Python script to analyze CSV files and create visualizations"

**Text Response Queries:**
- "Explain how machine learning works"
- "What is the difference between REST and GraphQL?"
- "Describe the software development lifecycle"

## Configuration

Edit `app/config.py` to customize:

- **API Keys**: Set via environment variables or `.env` file
- **Model Selection**: Choose default LLM model
- **Output Settings**: Configure output directory and file size limits
- **Code Generation**: Adjust thresholds and enable/disable features

## API Endpoints

### `GET /`
Main UI page

### `POST /api/query`
Process a query and generate output
- **Body**: `multipart/form-data`
  - `query` (string, required): User query
  - `file` (file, optional): Uploaded file

### `GET /api/download/{filename}`
Download generated output file

### `GET /api/query-templates`
Get list of available query templates

## Architecture

### Agent Logic

The `SimpleAgent` class:
1. Analyzes queries to determine if code generation is appropriate
2. Detects programming languages and frameworks
3. Generates codebases using LLM APIs (OpenAI/Anthropic/Google Gemini)
4. Falls back to basic templates if APIs are unavailable

### Output Management

- **Codebases**: Generated as ZIP files with proper directory structure
- **Text Responses**: Generated as TXT files with formatted content
- All outputs are stored in the `outputs/` directory

## Best Practices

- **Maintainable Code**: Modular structure with clear separation of concerns
- **Extensible Design**: Easy to add new features and integrations
- **Error Handling**: Comprehensive error handling throughout
- **Type Hints**: Python type hints for better code clarity
- **Documentation**: Inline comments and docstrings

## Troubleshooting

### API Key Issues
- Ensure your `.env` file is in the project root
- Verify API keys are correctly set
- Check API key permissions and quotas

### File Upload Issues
- Maximum file size: 10MB
- Supported formats: PDF, TXT, MD, DOCX
- Ensure files are not corrupted

### Output Generation Issues
- Check `outputs/` directory permissions
- Verify sufficient disk space
- Review application logs for errors

## Future Enhancements

Potential features for extension:
- Support for more file formats
- Additional LLM providers
- Code execution and testing
- Version control integration
- Multi-language support
- Advanced code analysis

## License

This project is open source and available for use and modification.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style and patterns
- New features include appropriate tests
- Documentation is updated

---

**SimpleAgent v1.0.0** - Built with FastAPI & AI


