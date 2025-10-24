cat > README.md << 'EOF'
# AI Log Analyzer

Python scripts for analyzing Jenkins build failures using Google Gemini AI.

## Scripts

### `analyze_log.py`
Standalone analyzer without GitHub integration.

**Usage:**
```bash
python3 analyze_log.py <log_file> [output_file]
```

**Example:**
```bash
python3 analyze_log.py build_log.txt analysis.txt
```

### `analyze_and_comment.py`
Full-featured analyzer that posts results to GitHub PR comments.

**Usage:**
```bash
python3 analyze_and_comment.py <log_file> <repo_name> <pr_number> [output_file]
```

## Requirements

- Python 3.8+
- Google Gemini API key
- GitHub Personal Access Token (for analyze_and_comment.py)

## Installation
```bash
pip install -r requirements.txt
```

## Environment Variables
```bash
export GEMINI_API_KEY="your_gemini_api_key"
export GITHUB_TOKEN="your_github_token"
```
EOF