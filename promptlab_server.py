#!/usr/bin/env python3
import logging
import os
import sys
import json
import traceback
import asyncio
from typing import Dict, Any, List, Optional

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import LangGraph and Vertex AI components
from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage

# Import MLflow components
import mlflow
from mlflow.tracking import MlflowClient

# --- Logging Setup ---
# Check debug mode from environment
debug_mode = os.getenv('PROMPTLAB_DEBUG', 'false').lower() == 'true'
log_level = logging.DEBUG if debug_mode else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("promptlab-server")

# --- Environment Setup ---
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    logger.info(f"Loaded environment variables from: {dotenv_path}")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')

# --- Global Variables ---
llm = None
mlflow_client = None
available_prompts = {}

# --- Initialize Components ---
async def initialize_components():
    global llm, mlflow_client, available_prompts
    
    try:
        # Initialize Vertex AI
        if not GCP_PROJECT_ID:
            logger.error("GCP_PROJECT_ID is not set in .env file.")
            return False
        
        llm = ChatVertexAI(
            project=GCP_PROJECT_ID, 
            location=GCP_LOCATION, 
            model_name="gemini-2.5-pro", 
            temperature=0.1, 
            convert_system_message_to_human=True
        )
        logger.info(f"ChatVertexAI initialized for model 'gemini-2.5-pro'.")
        
        # Initialize MLflow
        if not MLFLOW_TRACKING_URI:
            logger.error("MLFLOW_TRACKING_URI not set.")
            return False
        
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow_client = MlflowClient()
        logger.info(f"MLflow client configured for: {MLFLOW_TRACKING_URI}")
        
        # Load prompts
        available_prompts = await load_all_prompts()
        logger.info(f"Loaded {len(available_prompts)} prompts from MLflow.")
        
        return True
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        return False

# --- Core Functions ---
async def load_all_prompts() -> Dict[str, Any]:
    """Load all prompts from MLflow registry or use fallback prompts"""
    prompts = {}
    
    # 首先尝试从MLflow加载
    if mlflow_client:
        try:
            # Try to load known prompt names with specific versions
            known_prompts = {
                "essay_prompt": "9",
                "email_prompt": "9", 
                "technical_prompt": "9",
                "creative_prompt": "9",
                "test_prompt": "1"
            }
            
            for name, version in known_prompts.items():
                try:
                    prompt = mlflow.genai.load_prompt(f"prompts:/{name}/{version}")
                    prompts[name] = {
                        "template": prompt.template,
                        "tags": getattr(prompt, "tags", {}),
                        "version": getattr(prompt, "version", version)
                    }
                except Exception as e:
                    logger.debug(f"Prompt {name} version {version} not found: {e}")
                    continue
            
            if prompts:
                logger.info(f"Successfully loaded {len(prompts)} prompts from MLflow.")
                return prompts
        except Exception as e:
            logger.error(f"Failed to load prompts from MLflow URI '{MLFLOW_TRACKING_URI}': {e}")
    
    # 如果MLflow加载失败，使用内置的示例提示词
    logger.info("Using fallback built-in prompts")
    prompts = {
        "essay_prompt": {
            "template": "Write a well-structured essay on {{ topic }} that includes:\n- A compelling introduction that provides context and states your thesis\n- 2-3 body paragraphs, each with a clear topic sentence and supporting evidence\n- Logical transitions between paragraphs that guide the reader\n- A conclusion that synthesizes your main points and offers final thoughts\n\nThe essay should be informative, well-reasoned, and demonstrate critical thinking.",
            "tags": {"task": "writing", "type": "essay"},
            "version": "fallback"
        },
        "email_prompt": {
            "template": "Write a {{ formality }} email to my {{ recipient_type }} about {{ topic }} that includes:\n- A clear subject line\n- Appropriate greeting\n- Brief introduction stating the purpose\n- Main content in short paragraphs\n- Specific action items or requests clearly highlighted\n- Professional closing\n\nThe tone should be {{ tone }}.",
            "tags": {"task": "writing", "type": "email"},
            "version": "fallback"
        },
        "technical_prompt": {
            "template": "Provide a clear technical explanation of {{ topic }} for a {{ audience }} audience that:\n- Begins with a conceptual overview that anyone can understand\n- Uses analogies or real-world examples to illustrate complex concepts\n- Defines technical terminology when first introduced\n- Gradually increases in technical depth\n- Includes practical applications or implications where relevant\n- Addresses common misunderstandings or misconceptions",
            "tags": {"task": "explanation", "type": "technical"},
            "version": "fallback"
        },
        "creative_prompt": {
            "template": "Write a creative {{ genre }} about {{ topic }} that:\n- Uses vivid sensory details and imagery\n- Develops interesting and multidimensional characters (if applicable)\n- Creates an engaging narrative arc with tension and resolution\n- Establishes a distinct mood, tone, and atmosphere\n- Employs figurative language to enhance meaning\n- Avoids clichés and predictable elements",
            "tags": {"task": "writing", "type": "creative"},
            "version": "fallback"
        }
    }
    
    logger.info(f"Loaded {len(prompts)} fallback prompts.")
    return prompts

async def match_prompt(query: str) -> Dict[str, Any]:
    """Match user query to the best prompt template"""
    global available_prompts
    if not available_prompts or not llm:
        status = "no_prompts_available" if not available_prompts else "no_llm"
        return {"status": status, "prompt_name": None}
    
    # Create prompt list for LLM
    prompt_list = []
    for name, prompt_data in available_prompts.items():
        task_type = prompt_data.get("tags", {}).get("type", "general")
        prompt_list.append(f"- **{name}**: For tasks related to {task_type}")
    
    # Create matching prompt
    prompt_text = f'''**User Query:** "{query}"

**Available Tools:**
{chr(10).join(prompt_list)}

**Task:** Choose the best tool for the query. Respond with a single JSON object: {{"prompt_name": "tool_name_or_none"}}'''
    
    try:
        response = await llm.ainvoke(prompt_text)
        match_result = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
        prompt_name = match_result.get("prompt_name")
        
        if prompt_name and prompt_name in available_prompts:
            return {"status": "matched", "prompt_name": prompt_name}
        else:
            return {"status": "no_match", "prompt_name": None}
            
    except Exception as e:
        logger.error(f"Error in prompt matching: {e}")
        return {"status": "error", "prompt_name": None, "error": str(e)}

async def enhance_query(query: str, prompt_name: str) -> str:
    """Apply the selected prompt template to enhance the query"""
    global available_prompts
    if prompt_name not in available_prompts:
        return query
    
    template = available_prompts[prompt_name]["template"]
    try:
        # Simple template formatting - replace {{topic}} with the query
        enhanced = template.replace("{{ topic }}", query).replace("{{topic}}", query)
        return enhanced
    except Exception as e:
        logger.error(f"Error enhancing query: {e}")
        return query

# --- MCP Server Setup ---
server = Server("promptlab")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="optimize_query",
            description="Optimize a user query by matching it to the best prompt template and enhancing it",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user query to optimize"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_prompts",
            description="List all available prompt templates in the MLflow registry",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="reload_prompts",
            description="Reload prompt templates from MLflow registry",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls"""
    global available_prompts, llm, mlflow_client
    try:
        if name == "optimize_query":
            query = arguments.get("query", "")
            if not query:
                return [TextContent(type="text", text="Error: Query parameter is required")]
            
            # Match prompt
            match_result = await match_prompt(query)
            
            if match_result["status"] == "matched":
                prompt_name = match_result["prompt_name"]
                enhanced_query = await enhance_query(query, prompt_name)
                
                result = {
                    "original_query": query,
                    "matched_prompt": prompt_name,
                    "enhanced_query": enhanced_query,
                    "status": "success"
                }
            else:
                result = {
                    "original_query": query,
                    "enhanced_query": query,
                    "status": "no_match",
                    "message": "No suitable prompt template found, returning original query"
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "list_prompts":
            # Debug: Check available_prompts status
            logger.debug(f"available_prompts type: {type(available_prompts)}")
            logger.debug(f"available_prompts content: {available_prompts}")
            
            prompt_list = []
            for prompt_name, data in available_prompts.items():
                prompt_list.append({
                    "name": prompt_name,
                    "tags": data.get("tags", {}),
                    "version": data.get("version", "unknown")
                })
            
            result = {
                "prompts": prompt_list,
                "count": len(prompt_list)
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "reload_prompts":
            globals()['available_prompts'] = await load_all_prompts()
            available_prompts = globals()['available_prompts']
            
            result = {
                "status": "success",
                "message": f"Reloaded {len(available_prompts)} prompts from MLflow",
                "count": len(available_prompts)
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
    
    except Exception as e:
        logger.error(f"Error in tool call '{name}': {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# --- Main Function ---
async def main():
    """Main entry point"""
    logger.info("Starting PromptLab MCP Server...")
    
    # Initialize components
    if not await initialize_components():
        logger.error("Failed to initialize components. Exiting.")
        sys.exit(1)
    
    logger.info("PromptLab MCP Server initialized successfully.")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())