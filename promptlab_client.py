import argparse
import httpx
import json
import sys
import textwrap

# Define the server URL
SERVER_URL = "http://127.0.0.1:8000"

# ANSI color codes for pretty printing
class Colors:
    HEADER = '\033[95m'; BLUE = '\033[94m'; GREEN = '\033[92m'
    FAIL = '\033[91m'; ENDC = '\033[0m'; BOLD = '\033[1m'

def pretty_print_result(data):
    """Prints the final result in a readable format."""
    result = data.get('result', {})
    if not result:
        print(f"{Colors.FAIL}Error: No 'result' key in server response.{Colors.ENDC}\n{data}")
        return

    print(f"\n{Colors.GREEN}{Colors.BOLD}--- PromptLab Analysis ---{Colors.ENDC}")
    print(f"{Colors.HEADER}Original Query:{Colors.ENDC} {result.get('original_query')}")

    if "error" in result:
        print(f"\n{Colors.FAIL}Server Error: {result['error']}{Colors.ENDC}")
        return

    match_info = result.get('prompt_match', {})
    match_status = match_info.get('status', 'unknown')
    
    print(f"{Colors.BLUE}Prompt Match Status:{Colors.ENDC} {match_status}")
    if match_status == 'matched':
        print(f"{Colors.BLUE}Matched Prompt:{Colors.ENDC} {match_info.get('prompt_name')}")

    if result.get('enhanced'):
        print(f"\n{Colors.GREEN}{Colors.BOLD}Enhanced Query:{Colors.ENDC}")
        print("-" * 80); print(result.get('final_query')); print("-" * 80)
    else:
        print(f"\n{Colors.BLUE}Query was not enhanced.{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description="A client for the PromptLab HTTP server.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("query", nargs="?", default=None, help="The user query to process.")
    group.add_argument("--list", action="store_true", help="List all available prompts.")
    args = parser.parse_args()

    tool_name = "list_prompts" if args.list else "optimize_query"
    payload = {} if args.list else {"query": args.query}

    try:
        with httpx.Client() as client:
            print(f"Sending request to {SERVER_URL}/tools/{tool_name}...")
            response = client.post(f"{SERVER_URL}/tools/{tool_name}", json=payload, timeout=120.0)
            response.raise_for_status()
            
            response_data = response.json()
            if args.list:
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
            else:
                pretty_print_result(response_data)
    except httpx.ConnectError:
        print(f"{Colors.FAIL}Connection Error: Could not connect to the server at {SERVER_URL}. Is it running?{Colors.ENDC}")
    except httpx.HTTPStatusError as e:
        print(f"{Colors.FAIL}HTTP Error: {e.response.status_code}. Response: {e.response.text}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()