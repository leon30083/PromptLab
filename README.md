# PromptLab: MCP Server for AI Query Enhancement

PromptLab is a **Model Context Protocol (MCP) server** that transforms basic user queries into optimized prompts using MLflow Prompt Registry and Google's Gemini 2.5 Pro model. It intelligently matches user requests to the most appropriate prompt template and enhances them for better AI responses.

## 🔍 Overview

PromptLab is designed as a standard MCP tool that can be integrated into any MCP-compatible application (Claude Desktop, Cline, etc.):

- **🤖 MCP Standard Compliance**: Full Model Context Protocol implementation
- **🧠 Gemini 2.5 Pro Integration**: Powered by Google's latest AI model
- **📚 Centralized Prompt Management**: Store, version, and manage prompts in MLflow
- **🎯 Dynamic Matching**: Intelligently match user queries to the best prompt template
- **📈 Version Control**: Track prompt history with production and archive aliases
- **🔧 Extensible**: Easily add new prompt types without code changes

## 🏗️ Architecture

The system consists of three main components:

1. **Prompt Registry** (`register_prompts.py`) - Tool for registering and managing prompts in MLflow
2. **Server** (`promptlab_server.py`) - Server with dynamic prompt matching and LangGraph workflow
3. **Client** (`promptlab_client.py`) - Lightweight client for processing user queries

### Workflow Process

![PromptLab Workflow](promptlab_architecture.png)

1. **Prompt Registration**: Register prompt templates in MLflow with versioning and aliasing
2. **Prompt Loading**: Server loads all available prompts from MLflow at startup
3. **Query Submission**: User submits a natural language query via the client
4. **Intelligent Matching**: LLM analyzes the query and selects the most appropriate prompt template
5. **Parameter Extraction**: System extracts required parameters from the query
6. **Template Application**: Selected template is applied with extracted parameters
7. **Validation & Adjustment**: Enhanced prompt is validated and adjusted if needed
8. **Response Generation**: Optimized prompt produces a high-quality response

## 📂 Code Structure

```
promptlab/
├── promptlab_server.py            # Main server with LangGraph workflow
├── promptlab_client.py            # Client for processing queries
├── register_prompts.py            # MLflow prompt management tool
├── requirements.txt               # Project dependencies
├── advanced_prompts.json          # Additional prompt templates
└── README.md                      # Project documentation
```

### Core Components:

#### `register_prompts.py`
- **Purpose**: Manages prompts in MLflow Registry
- **Key Functions**:
  - `register_prompt()`: Register a new prompt or version
  - `update_prompt()`: Update an existing prompt (archives previous production)
  - `list_prompts()`: List all registered prompts
  - `register_from_file()`: Register multiple prompts from JSON
  - `register_sample_prompts()`: Initialize with standard prompts

#### `promptlab_server.py`
- **Purpose**: Processes queries using LangGraph workflow
- **Key Components**:
  - `load_all_prompts()`: Loads prompts from MLflow
  - `match_prompt()`: Matches queries to appropriate templates
  - `enhance_query()`: Applies selected template
  - `validate_query()`: Validates enhanced queries
  - `LangGraph workflow`: Orchestrates the query enhancement process

#### `promptlab_client.py`
- **Purpose**: Provides user interface to the service
- **Key Features**:
  - Process queries with enhanced prompts
  - List available prompts
  - Display detailed prompt matching information

## 🛠️ Technology Stack

- **MCP (Model Context Protocol)**: Standard protocol for AI tool integration
- **Google Vertex AI**: Gemini 2.5 Pro model for intelligent prompt matching
- **MLflow**: Prompt registry and experiment tracking
- **LangGraph**: Workflow orchestration and state management
- **Python 3.12**: Core runtime environment
- **Rich**: Enhanced console output and formatting

## 📦 Installation & Setup

### Prerequisites
- Python 3.12+
- Google Cloud Platform account with Vertex AI enabled
- MLflow server (local or remote)
- MCP-compatible application (Claude Desktop, Cline, etc.)

### Step 1: Environment Setup

1. **Clone and navigate to the repository**:
   ```bash
   git clone https://github.com/iRahulPandey/PromptLab.git
   cd PromptLab
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Configuration

1. **Configure environment variables**:
   Create a `.env` file:
   ```env
   GCP_PROJECT_ID="your-gcp-project-id"
   GCP_LOCATION="us-central1"
   MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
   ```

2. **Set up Google Cloud authentication**:
   ```bash
   # Install Google Cloud CLI and authenticate
   gcloud auth application-default login
   ```

### Step 3: Start Services

1. **Start MLflow server** (in a separate terminal):
   ```bash
   mlflow server --host 127.0.0.1 --port 5000
   ```

2. **Register sample prompts**:
   ```bash
   python register_prompts.py register-samples
   ```

3. **Test the MCP server**:
   ```bash
   python test_mcp.py
   ```

### Registering Prompts

Before using PromptLab, you need to register prompts in MLflow:

```bash
# Register sample prompts (essay, email, technical, creative)
python register_prompts.py register-samples

# Register additional prompt types (recommended)
python register_prompts.py register-file --file advanced_prompts.json

# Verify registered prompts
python register_prompts.py list
```

### Step 4: MCP Client Configuration

1. **Add to your MCP client configuration**:
   
   For **Claude Desktop**, add to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "promptlab": {
         "command": "python",
         "args": ["e:\\User\\MCP\\PromptLab\\promptlab_server.py"],
         "cwd": "e:\\User\\MCP\\PromptLab",
         "env": {
           "GCP_PROJECT_ID": "your-gcp-project-id",
           "GCP_LOCATION": "us-central1",
           "MLFLOW_TRACKING_URI": "http://127.0.0.1:5000"
         }
       }
     }
   }
   ```

   For **Cline** or other MCP clients, use the provided `mcp.json` configuration file.

2. **Restart your MCP client** to load the new server.

## 🚀 Usage

### Available MCP Tools

Once configured, PromptLab provides these tools in your MCP client:

1. **`optimize_query`** - Enhance user queries with best-matched prompts
   - Input: Your natural language query
   - Output: Enhanced prompt optimized for AI responses

2. **`list_prompts`** - List all available prompt templates
   - Shows all registered prompts with their descriptions

3. **`reload_prompts`** - Reload prompts from MLflow registry
   - Refreshes the prompt cache from MLflow

### Example Usage in Claude Desktop

1. **Optimize a query**:
   ```
   User: "Help me write a blog post about AI"
   PromptLab: [Uses blog_prompt template to enhance the request]
   ```

2. **List available prompts**:
   ```
   User: "What prompts are available?"
   PromptLab: [Shows all registered prompt templates]
   ```

### Command Line Usage (Development)

```bash
# Register prompts from JSON file
python register_prompts.py register-from-file advanced_prompts.json

# Register individual prompt
python register_prompts.py register "My Prompt" "Template: {input}" "Added new prompt"

# List all prompts
python register_prompts.py list

# Get prompt details
python register_prompts.py details "essay_prompt"

# Test the MCP server
python test_mcp.py
```

## 📋 Prompt Management

### Available Prompt Types

PromptLab supports a wide range of prompt types:

| Prompt Type | Description | Example Use Case |
|------------|-------------|-----------------|
| essay_prompt | Academic writing | Research papers, analyses |
| email_prompt | Email composition | Professional communications |
| technical_prompt | Technical explanations | Concepts, technologies |
| creative_prompt | Creative writing | Stories, poems, fiction |
| code_prompt | Code generation | Functions, algorithms |
| summary_prompt | Content summarization | Articles, documents |
| analysis_prompt | Critical analysis | Data, texts, concepts |
| qa_prompt | Question answering | Context-based answers |
| social_media_prompt | Social media content | Platform-specific posts |
| blog_prompt | Blog article writing | Online articles |
| report_prompt | Formal reports | Business, technical reports |
| letter_prompt | Formal letters | Cover, recommendation letters |
| presentation_prompt | Presentation outlines | Slides, talks |
| review_prompt | Reviews | Products, media, services |
| comparison_prompt | Comparisons | Products, concepts, options |
| instruction_prompt | How-to guides | Step-by-step instructions |
| custom_prompt | Customizable template | Specialized use cases |

### Registering New Prompts

You can register new prompts in several ways:

#### 1. From Command Line

```bash
python register_prompts.py register \
  --name "new_prompt" \
  --template "Your template with {{ variables }}" \
  --message "Initial version" \
  --tags '{"type": "custom", "task": "specialized"}'
```

#### 2. From a Template File

```bash
# Create a text file with your template
echo "Template content with {{ variables }}" > template.txt

# Register using the file
python register_prompts.py register \
  --name "long_prompt" \
  --template template.txt \
  --message "Complex template"
```

#### 3. From a JSON File

Create a JSON file with multiple prompts:

```json
{
  "prompts": [
    {
      "name": "prompt_name",
      "template": "Template with {{ variables }}",
      "commit_message": "Description",
      "tags": {"type": "category", "task": "purpose"}
    }
  ]
}
```

Then register them:

```bash
python register_prompts.py register-file --file your_prompts.json
```

### Updating Existing Prompts

When you update an existing prompt, the system automatically:
1. Archives the previous production version
2. Sets the new version as production

```bash
python register_prompts.py update \
  --name "essay_prompt" \
  --template "New improved template with {{ variables }}" \
  --message "Enhanced clarity and structure"
```

### Viewing Prompt Details

```bash
# List all prompts
python register_prompts.py list

# View detailed information about a specific prompt
python register_prompts.py details --name "essay_prompt"
```

## 🛠️ Advanced Usage

### Template Variables

Templates use variables in `{{ variable }}` format:

```
Write a {{ formality }} email to my {{ recipient_type }} about {{ topic }} that includes:
- A clear subject line
- Appropriate greeting
...
```

When matching a query, the system automatically extracts values for these variables.

### Production and Archive Aliases

Each prompt can have different versions with aliases:
- **production**: The current active version (used by default)
- **archived**: Previous production versions

This allows for:
- Rolling back to previous versions if needed
- Tracking the history of prompt changes

### Custom Prompt Registration

For specialized use cases, you can create highly customized prompts:

```bash
python register_prompts.py register \
  --name "specialized_prompt" \
  --template "You are a {{ role }} with expertise in {{ domain }}. Create a {{ document_type }} about {{ topic }} that demonstrates {{ quality }}." \
  --message "Specialized template" \
  --tags '{"type": "custom", "task": "specialized", "domain": "finance"}'
```

## 🔧 Troubleshooting

### Common Issues

1. **"GCP authentication failed"**
   ```bash
   # Re-authenticate with Google Cloud
   gcloud auth application-default login
   ```

2. **"MLflow connection refused"**
   ```bash
   # Make sure MLflow server is running
   mlflow server --host 127.0.0.1 --port 5000
   ```

3. **"No prompts found"**
   ```bash
   # Register sample prompts
   python register_prompts.py register-samples
   ```

4. **"MCP server not responding"**
   ```bash
   # Test the server
   python test_mcp.py
   ```

5. **"Virtual environment not activated"**
   ```bash
   # Windows
   .\venv\Scripts\Activate.ps1
   # Linux/Mac
   source venv/bin/activate
   ```

### Debug Mode

For detailed logging, set the environment variable:
```bash
export LOG_LEVEL="DEBUG"
```

### No Matching Prompt Found

If the system can't match a query to any prompt template, it will:
1. Log a message that no match was found
2. Use the original query without enhancement
3. Still generate a response

You can add more diverse prompt templates to improve matching.

### LLM Connection Issues

If the Gemini service is unavailable, the system falls back to:
1. Keyword-based matching for prompt selection
2. Simple parameter extraction
3. Basic prompt enhancement

This ensures the system remains functional even without LLM access.

## 📁 Project Structure

```
PromptLab/
├── promptlab_server.py      # MCP server with Gemini 2.5 Pro integration
├── promptlab_client.py      # Legacy HTTP client (for reference)
├── register_prompts.py      # MLflow prompt registration utilities
├── start_mcp.py            # MCP server startup script
├── test_mcp.py             # MCP server testing script
├── advanced_prompts.json    # Sample prompt templates
├── mcp.json                # MCP client configuration
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration
├── 测试流程.md              # Testing workflow (Chinese)
└── README.md               # This documentation
```

## 🚀 Quick Start Checklist

- [ ] Python 3.12+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with GCP credentials
- [ ] Google Cloud authentication completed
- [ ] MLflow server running (`mlflow server --host 127.0.0.1 --port 5000`)
- [ ] Sample prompts registered (`python register_prompts.py register-samples`)
- [ ] MCP server tested (`python test_mcp.py`)
- [ ] MCP client configured (Claude Desktop/Cline)
- [ ] Client restarted to load the new server

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎉 Congratulations!** You now have a fully functional MCP server that enhances AI queries using intelligent prompt matching with Gemini 2.5 Pro and MLflow integration.