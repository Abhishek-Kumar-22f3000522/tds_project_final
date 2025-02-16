# LLM-based Automation Agent

This project implements an automation agent that uses LLMs to parse and execute various tasks. The agent exposes an API that accepts plain-English task descriptions and executes them accordingly.

## Features

- Task parsing using LLM
- Secure file operations within /data directory
- Support for various operations including:
  - File formatting
  - Date analysis
  - JSON processing
  - Log file analysis
  - Email extraction
  - Credit card number extraction
  - Similarity analysis
  - Database operations
  - API interactions
  - Git operations
  - And more...

## Setup

1. Clone the repository
2. Build the Docker image:
   ```bash
   docker build -t automation-agent .
   ```
3. Run the container:
   ```bash
   docker run -e AIPROXY_TOKEN=your_token_here -p 8000:8000 automation-agent
   ```

## API Endpoints

- `POST /run?task=<task description>`: Execute a task
- `GET /read?path=<file path>`: Read file contents

## Usage Examples

```bash
# Count Wednesdays in a date file
curl -X POST "http://localhost:8000/run?task=Count the number of Wednesdays in /data/dates.txt and write to /data/result.txt"

# Read the result
curl "http://localhost:8000/read?path=/data/result.txt"
```

