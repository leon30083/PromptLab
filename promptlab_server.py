from mcp.server.fastmcp import FastMCP
import logging
import os
import asyncio
import sys
import json
import traceback
from typing import Dict, Any, TypedDict, List, Optional, Tuple

# Import LangGraph components
from langgraph.graph import StateGraph, END, START
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage

# Import MLflow components
import mlflow
from mlflow.entities import Prompt

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("promptlab-server")

# ##################################################################
# # FINAL FIX: Make .env loading robust
# ##################################################################
from dotenv import load_dotenv
# Explicitly find and load the .env file from the script's directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    logger.info(f"Loaded environment variables from: {dotenv_path}")
else:
    logger.warning(".env file not found, relying on system environment variables.")
# ##################################################################

# Configuration for Vertex AI and MLflow
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')

# Define state schema
class QueryState(TypedDict, total=False):
    user_query: str
    prompt_match: Dict[str, Any]
    enhanced_query: str
    final_query: str
    available_prompts: Dict[str, Prompt]
    should_skip_enhance: bool
    parameters: Dict[str, Any]

# Initialize MCP server
mcp = FastMCP(
    name="promptlab",
    instructions="AI query enhancement service using Vertex AI and MLflow."
)

# Initialize LLM via Vertex AI
llm = None
try:
    if not GCP_PROJECT_ID:
        logger.error("GCP_PROJECT_ID is not set in .env file.")
    else:
        llm = ChatVertexAI(
            project=GCP_PROJECT_ID,
            location=GCP_LOCATION,
            model_name="gemini-2.5-pro",
            temperature=0.1,
            convert_system_message_to_human=True
        )
        logger.info(f"ChatVertexAI initialized for model 'gemini-2.5-pro' in project '{GCP_PROJECT_ID}'")
except Exception as e:
    logger.error(f"Failed to initialize ChatVertexAI: {e}", exc_info=True)

def setup_mlflow_connection():
    if not MLFLOW_TRACKING_URI:
        logger.error("MLFLOW_TRACKING_URI is not set in .env file.")
        return False
    os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    logger.info(f"Using MLflow tracking URI: {MLFLOW_TRACKING_URI}")
    return True

def load_all_prompts() -> Dict[str, Prompt]:
    prompts = {}
    if not setup_mlflow_connection():
        return prompts
        
    client = mlflow.tracking.MlflowClient()
    registered_models = client.search_registered_models()
    for model in registered_models:
        try:
            prompt = mlflow.load_prompt(f"prompts:/{model.name}")
            prompts[model.name] = prompt
            logger.info(f"Loaded prompt '{model.name}' version {prompt.version}")
        except Exception as e:
            logger.warning(f"Could not load prompt '{model.name}': {e}")
    logger.info(f"Loaded {len(prompts)} prompts from MLflow.")
    return prompts

# --- Workflow Node Definitions ---

async def load_prompts_node(state: QueryState) -> QueryState:
    logger.info("Node: load_prompts")
    try:
        prompts = load_all_prompts()
        return {**state, "available_prompts": prompts}
    except Exception as e:
        logger.error(f"Error loading prompts: {e}", exc_info=True)
        return {**state, "available_prompts": {}}

async def match_prompt_node(state: QueryState) -> QueryState:
    logger.info("Node: match_prompt")
    query = state['user_query']
    available_prompts = state.get('available_prompts', {})

    if not available_prompts or not llm:
        status = "no_prompts_available" if not available_prompts else "no_llm"
        logger.warning(f"Skipping enhancement: {status}")
        return {**state, "should_skip_enhance": True, "prompt_match": {"status": status, "reasoning": f"Server status: {status}"}}

    prompt_list_for_llm = [
        f"- **{name}**: For tasks related to {prompt.tags.get('type', 'general use')}."
        for name, prompt in available_prompts.items()
    ]

    matching_prompt_text = f"""
    As a routing assistant, select the single best tool for the user's query from the list below.

    **User Query:** "{query}"

    **Available Tools:**
    {os.linesep.join(prompt_list_for_llm)}

    **Instructions:**
    1.  Analyze the user's intent.
    2.  Choose the best tool. If none fit, you MUST respond with "none".
    3.  Output a single JSON object with "prompt_name" (the tool name or "none"), "reasoning" (your brief explanation), and "parameters" (a dictionary of extracted values from the query).
    """
    
    try:
        response = await llm.ainvoke([HumanMessage(content=matching_prompt_text)])
        cleaned_response = response.content.strip().replace("```json", "").replace("```", "").strip()
        match_result = json.loads(cleaned_response)
        
        prompt_name = match_result.get("prompt_name")
        if prompt_name and prompt_name != "none" and prompt_name in available_prompts:
            logger.info(f"LLM Matched to '{prompt_name}'.")
            return {
                **state,
                "prompt_match": {"status": "matched", **match_result},
                "parameters": match_result.get("parameters", {}),
                "should_skip_enhance": False
            }
        else:
            logger.warning(f"LLM found no suitable prompt. Reasoning: {match_result.get('reasoning')}")
            return {**state, "should_skip_enhance": True, "prompt_match": {"status": "no_match", "reasoning": match_result.get('reasoning')}}
    except Exception as e:
        logger.error(f"Error during LLM matching: {e}", exc_info=True)
        return {**state, "should_skip_enhance": True, "prompt_match": {"status": "error", "reasoning": traceback.format_exc()}}

async def enhance_query_node(state: QueryState) -> QueryState:
    logger.info("Node: enhance_query")
    if state.get("should_skip_enhance"):
        return {**state, "final_query": state["user_query"]}

    prompt_name = state["prompt_match"]["prompt_name"]
    prompt_template = state["available_prompts"][prompt_name].template
    parameters = state.get("parameters", {})
    
    import re
    required_vars = re.findall(r'{{(.*?)}}', prompt_template)
    for var in required_vars:
        parameters.setdefault(var, f"[{var.replace('_', ' ').title()}]")

    enhanced_query = prompt_template.format(**parameters)
    return {**state, "enhanced_query": enhanced_query, "final_query": enhanced_query}

async def final_result_node(state: QueryState) -> QueryState:
    logger.info("Node: final_result")
    return {**state}

def should_enhance_edge(state: QueryState) -> str:
    return "enhance_query" if not state.get("should_skip_enhance") else "final_result"

# --- Workflow Definition ---
workflow = StateGraph(QueryState)
workflow.add_node("load_prompts", load_prompts_node)
workflow.add_node("match_prompt", match_prompt_node)
workflow.add_node("enhance_query", enhance_query_node)
workflow.add_node("final_result", final_result_node)

workflow.set_entry_point("load_prompts")
workflow.add_edge("load_prompts", "match_prompt")
workflow.add_conditional_edges("match_prompt", should_enhance_edge, {
    "enhance_query": "enhance_query",
    "final_result": "final_result"
})
workflow.add_edge("enhance_query", "final_result")
workflow.add_edge("final_result", END)
workflow_app = workflow.compile()

# --- MCP Tool Definition ---

@mcp.tool()
async def optimize_query(query: str) -> Dict[str, Any]:
    logger.info(f"Executing 'optimize_query' tool for query: '{query}'")
    if not llm:
        return {"error": "LLM not initialized on server.", "enhanced": False, "original_query": query}
        
    try:
        initial_state = {"user_query": query}
        final_state = await workflow_app.ainvoke(initial_state)
        
        response = {
            "original_query": query,
            "prompt_match": final_state.get("prompt_match", {"status": "unknown"}),
            "enhanced": not final_state.get("should_skip_enhance", True),
            "final_query": final_state.get("final_query", query),
        }
        logger.info("Workflow finished successfully.")
        return response
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"An unhandled error occurred in the workflow:\n{error_details}")
        return {"original_query": query, "enhanced": False, "error": error_details}

@mcp.tool()
async def list_prompts() -> Dict[str, Any]:
    logger.info("Executing 'list_prompts' tool.")
    try:
        prompts = load_all_prompts()
        prompts_list = [{"name": name, "version": p.version, "tags": p.tags} for name, p in prompts.items()]
        return {"prompts": prompts_list, "count": len(prompts_list)}
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"An error occurred in list_prompts:\n{error_details}")
        return {"error": error_details, "prompts": []}

if __name__ == "__main__":
    if llm is None:
        logger.error("LLM could not be initialized. Server is shutting down.")
        sys.exit(1)
    logger.info("Starting PromptLab server...")
    mcp.run(transport="stdio")