{
  "mcpServers": {
    "promptlab": {
      "command": "ssh",
      "args": [
        "ubuntu@13.213.28.32",
        "cd /home/ubuntu/PromptLab && python enhanced_promptlab_server.py"
      ],
      "env": {
        "MLFLOW_TRACKING_URI": "http://localhost:5000"
      }
    }
  }
}