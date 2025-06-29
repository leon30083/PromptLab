#!/usr/bin/env python
import os
import argparse
import logging
import json
import mlflow
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mlflow-prompt-registry")

# Set up environment variables
from dotenv import load_dotenv
load_dotenv()
os.environ["MLFLOW_TRACKING_URI"] = os.getenv('MLFLOW_TRACKING_URI')

# MLflow connection setup
def setup_mlflow_connection():
    """Setup connection to MLflow server."""
    # Set MLflow tracking URI if not already set
    if not os.environ["MLFLOW_TRACKING_URI"]:
        mlflow_uri = os.path.abspath("./mlruns")
        mlflow.set_tracking_uri(mlflow_uri)
        logger.info(f"Set MLflow tracking URI to local directory: {mlflow_uri}")
    else:
        mlflow_uri = os.environ["MLFLOW_TRACKING_URI"]
        mlflow.set_tracking_uri(mlflow_uri)
        logger.info(f"Using MLflow tracking URI: {os.getenv('MLFLOW_TRACKING_URI')}")

def register_prompt(
    name: str, 
    template: str, 
    commit_message: str = "Initial commit", 
    tags: Optional[Dict[str, str]] = None, 
    set_as_production: bool = True
) -> Dict[str, Any]:
    """
    Register a prompt in MLflow Prompt Registry.
    
    Args:
        name: Name of the prompt
        template: Template text with variables in {{ variable }} format
        commit_message: Description of the prompt or changes
        tags: Optional key-value pairs for categorization
        set_as_production: Whether to set this version as the production alias
        
    Returns:
        Dictionary with registration details
    """
    try:
        # Check if the prompt already exists with a production alias
        previous_production_version = None
        try:
            # This FutureWarning indicates the API is changing, our code is fine for now
            previous_prompt = mlflow.load_prompt(f"prompts:/{name}@production")
            previous_production_version = previous_prompt.version
            logger.info(f"Found existing production version {previous_production_version} for '{name}'")
        except Exception:
            logger.info(f"No existing production version found for '{name}'")
        
        # This FutureWarning indicates the API is changing, our code is fine for now
        # MODIFICATION: Removed the outdated 'version_metadata' argument
        prompt = mlflow.register_prompt(
            name=name,
            template=template,
            commit_message=commit_message,
            tags=tags or {}
        )
        
        # Handle aliasing
        if set_as_production:
            # Archive the previous production version if it exists
            if previous_production_version is not None:
                # This FutureWarning indicates the API is changing, our code is fine for now
                mlflow.set_prompt_alias(name, "archived", previous_production_version)
                logger.info(f"Archived '{name}' version {previous_production_version}")
                
            # Set new version as production
            mlflow.set_prompt_alias(name, "production", prompt.version)
            logger.info(f"Set '{name}' version {prompt.version} as production alias")
        
        result = {
            "name": name,
            "version": prompt.version,
            "status": "success",
            "production": set_as_production
        }
        
        # Add archived information if applicable
        if previous_production_version is not None:
            result["previous_production"] = previous_production_version
            result["archived"] = True
            
        return result
    except Exception as e:
        logger.error(f"Failed to register prompt '{name}': {e}")
        return {
            "name": name,
            "status": "error",
            "error": str(e)
        }

def register_from_file(file_path: str, set_as_production: bool = True) -> Dict[str, Any]:
    """
    Register prompts from a JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict) or "prompts" not in data:
            raise ValueError("JSON file must contain a 'prompts' list")
        
        results = []
        for prompt_data in data["prompts"]:
            name = prompt_data.get("name")
            if not name:
                logger.warning("Skipping prompt without name")
                continue
                
            template = prompt_data.get("template")
            if not template:
                logger.warning(f"Skipping prompt '{name}' without template")
                continue
            
            result = register_prompt(
                name=name,
                template=template,
                commit_message=prompt_data.get("commit_message", "Registered from file"),
                tags=prompt_data.get("tags"),
                set_as_production=set_as_production
            )
            results.append(result)
        
        return {
            "status": "success",
            "file": file_path,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Failed to register prompts from file '{file_path}': {e}")
        return {
            "status": "error",
            "file": file_path,
            "error": str(e)
        }

def register_sample_prompts() -> Dict[str, Any]:
    """
    Register standard sample prompts for each content type.
    """
    results = []
    
    # Essay prompt
    essay_result = register_prompt(
        name="essay_prompt",
        template="""
        Write a well-structured essay on {{ topic }} that includes:
        - A compelling introduction that provides context and states your thesis
        - 2-3 body paragraphs, each with a clear topic sentence and supporting evidence
        - Logical transitions between paragraphs that guide the reader
        - A conclusion that synthesizes your main points and offers final thoughts
        
        The essay should be informative, well-reasoned, and demonstrate critical thinking.
        """,
        commit_message="Initial essay prompt",
        tags={"task": "writing", "type": "essay"}
    )
    results.append(essay_result)
    
    # Email prompt
    email_result = register_prompt(
        name="email_prompt",
        template="""
        Write a {{ formality }} email to my {{ recipient_type }} about {{ topic }} that includes:
        - A clear subject line
        - Appropriate greeting
        - Brief introduction stating the purpose
        - Main content in short paragraphs
        - Specific action items or requests clearly highlighted
        - Professional closing
        
        The tone should be {{ tone }}.
        """,
        commit_message="Initial email prompt",
        tags={"task": "writing", "type": "email"}
    )
    results.append(email_result)
    
    # Technical prompt
    technical_result = register_prompt(
        name="technical_prompt",
        template="""
        Provide a clear technical explanation of {{ topic }} for a {{ audience }} audience that:
        - Begins with a conceptual overview that anyone can understand
        - Uses analogies or real-world examples to illustrate complex concepts
        - Defines technical terminology when first introduced
        - Gradually increases in technical depth
        - Includes practical applications or implications where relevant
        - Addresses common misunderstandings or misconceptions
        """,
        commit_message="Initial technical prompt",
        tags={"task": "explanation", "type": "technical"}
    )
    results.append(technical_result)
    
    # Creative prompt
    creative_result = register_prompt(
        name="creative_prompt",
        template="""
        Write a creative {{ genre }} about {{ topic }} that:
        - Uses vivid sensory details and imagery
        - Develops interesting and multidimensional characters (if applicable)
        - Creates an engaging narrative arc with tension and resolution
        - Establishes a distinct mood, tone, and atmosphere
        - Employs figurative language to enhance meaning
        - Avoids clichés and predictable elements
        """,
        commit_message="Initial creative prompt",
        tags={"task": "writing", "type": "creative"}
    )
    results.append(creative_result)
    
    return {
        "status": "success",
        "registered": len(results),
        "results": results
    }

def list_prompts() -> Dict[str, Any]:
    """
    List all prompts in the MLflow Prompt Registry.
    """
    # This is a simplified list function. A more robust one might query the MLflow API differently.
    try:
        client = mlflow.tracking.MlflowClient()
        # This is a workaround as there is no direct API to list all prompt names.
        # We list registered models, which includes prompts.
        all_models = client.search_registered_models()
        prompts = [model.name for model in all_models if not model.name.startswith("runs:")]

        prompts_info = []
        for name in prompts:
            try:
                latest_prompt = mlflow.load_prompt(f"prompts:/{name}")
                prompts_info.append({
                    "name": name,
                    "latest_version": latest_prompt.version,
                    "tags": getattr(latest_prompt, "tags", {})
                })
            except Exception as e:
                logger.warning(f"Could not load details for prompt '{name}': {e}")


        return {
            "status": "success",
            "prompts": prompts_info,
            "count": len(prompts_info)
        }
    except Exception as e:
        logger.error(f"Failed to list prompts: {e}")
        return {
            "status": "error",
            "error": str(e),
            "prompts": []
        }

def get_prompt_details(name: str) -> Dict[str, Any]:
    # This function remains largely the same but simplified error handling.
    try:
        latest_prompt = mlflow.load_prompt(f"prompts:/{name}")
        production_prompt = None
        try:
            production_prompt = mlflow.load_prompt(f"prompts:/{name}@production")
        except:
            pass
        
        variables = []
        import re
        for match in re.finditer(r'{{([^{}]+)}}', latest_prompt.template):
            var_name = match.group(1).strip()
            variables.append(var_name)

        return {
            "name": name,
            "status": "success",
            "latest_version": latest_prompt.version,
            "production_version": production_prompt.version if production_prompt else None,
            "variables": variables,
            "tags": getattr(latest_prompt, "tags", {}),
            "latest_template": latest_prompt.template
        }
    except Exception as e:
        logger.error(f"Failed to get details for prompt '{name}': {e}")
        return {"name": name, "status": "error", "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="MLflow Prompt Registry Management")
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new prompt")
    register_parser.add_argument("--name", required=True)
    register_parser.add_argument("--template", required=True)
    register_parser.add_argument("--message", default="Initial commit")
    register_parser.add_argument("--tags", type=json.loads)
    
    # Register from file command
    file_parser = subparsers.add_parser("register-file", help="Register prompts from a JSON file")
    file_parser.add_argument("--file", required=True)
    
    # Register samples command
    subparsers.add_parser("register-samples", help="Register sample prompts")
    
    # List command
    subparsers.add_parser("list", help="List all prompts")
    
    # Details command
    details_parser = subparsers.add_parser("details", help="Get prompt details")
    details_parser.add_argument("--name", required=True)
    
    args = parser.parse_args()
    
    setup_mlflow_connection()
    
    if args.command == "register":
        result = register_prompt(name=args.name, template=args.template, commit_message=args.message, tags=args.tags)
        print(json.dumps(result, indent=2))
    
    elif args.command == "register-file":
        result = register_from_file(file_path=args.file)
        print(json.dumps(result, indent=2))
    
    elif args.command == "register-samples":
        result = register_sample_prompts()
        print(json.dumps(result, indent=2))
    
    elif args.command == "list":
        result = list_prompts()
        print(json.dumps(result, indent=2))
        
    elif args.command == "details":
        result = get_prompt_details(name=args.name)
        print(json.dumps(result, indent=2))
    
if __name__ == "__main__":
    main()