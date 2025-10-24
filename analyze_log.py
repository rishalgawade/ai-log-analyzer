#!/usr/bin/env python3
"""
Standalone Jenkins Build Log Analyzer using Google Gemini AI
Analyzes build failures without GitHub integration
"""

import os
import sys
import google.generativeai as genai
from datetime import datetime


def read_log_file(log_path):
    """Read the build log file"""
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"❌ Error: Log file not found at {log_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        sys.exit(1)


def analyze_with_gemini(log_content, max_chars=30000):
    """Send log content to Gemini API for analysis"""
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        return "❌ Error: GEMINI_API_KEY environment variable not set"

    # Truncate log if too long (keep the end where errors usually appear)
    if len(log_content) > max_chars:
        print(f"⚠️  Log truncated from {len(log_content):,} to {max_chars:,} characters")
        log_content = "...[earlier output truncated]...\n\n" + log_content[-max_chars:]

    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Craft the analysis prompt
        prompt = f"""
You are an expert DevOps engineer analyzing a Jenkins CI/CD build failure log.

Your task is to analyze this build log and provide:

## 🔍 Root Cause
Identify the PRIMARY reason for the build failure. Be specific and concise (2-3 sentences).

## 📍 Error Location
Point to the exact file, line number, command, or stage where the failure occurred.
Include the actual error message if present.

## 🔧 Recommended Fixes
Provide 3-5 ACTIONABLE steps to resolve this issue:
1. [First concrete step with specific commands if applicable]
2. [Second step]
3. [Third step]
etc.

## 💡 Prevention Tips
Suggest 2-3 best practices to prevent this issue in the future.

## 🔗 Additional Resources
If applicable, mention relevant documentation links or related issues.

Build Log to Analyze:
---
{log_content}
---

IMPORTANT:
- Be technical but clear
- Focus on actionable insights
- Use bullet points for readability
- Include code examples when relevant
- Format response in clean Markdown
"""

        print("🤖 Analyzing build log with Gemini AI...")
        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        error_analysis = f"""
❌ **Error During AI Analysis**
```
{str(e)}
```

**Possible Causes:**
- Invalid or expired API key
- Network connectivity issues  
- API rate limit exceeded
- Gemini service temporarily unavailable

**Troubleshooting Steps:**
1. Verify GEMINI_API_KEY environment variable is set correctly
2. Check your API key at: https://aistudio.google.com/app/apikey
3. Ensure you have internet connectivity
4. Check Gemini API status
5. Review API usage limits on your account

**Manual Log Review:**
Please review the build log manually to identify:
- Error messages (lines containing "ERROR", "FAILED", "Exception")
- Exit codes (non-zero values)
- Stack traces
- Missing dependencies
"""
        return error_analysis


def save_analysis(analysis_text, output_path):
    """Save the AI analysis to a file"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("🤖 AI-POWERED BUILD FAILURE ANALYSIS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Analyzer: Jenkins AI Log Analyzer\n")
            f.write(f"AI Model: Google Gemini 2.0 Flash\n")
            f.write("=" * 80 + "\n\n")
            f.write(analysis_text)
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("End of Analysis\n")
            f.write("=" * 80 + "\n")

        print(f"✅ Analysis saved to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving analysis: {e}")
        return False


def display_help():
    """Display usage information"""
    help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  Jenkins AI Log Analyzer - Standalone                      ║
╚════════════════════════════════════════════════════════════════════════════╝

DESCRIPTION:
    Analyzes Jenkins build failure logs using Google Gemini AI to provide
    root cause analysis, error location, recommended fixes, and prevention tips.

USAGE:
    python3 analyze_log.py <log_file> [output_file]

ARGUMENTS:
    log_file     (required)  Path to the Jenkins build log file
    output_file  (optional)  Path for analysis output (default: analysis.txt)

ENVIRONMENT VARIABLES:
    GEMINI_API_KEY  (required)  Your Google Gemini API key
                                Get from: https://aistudio.google.com/app/apikey

EXAMPLES:
    # Basic usage
    python3 analyze_log.py build_log.txt

    # Specify custom output file
    python3 analyze_log.py build_log.txt my_analysis.txt

    # With environment variable
    GEMINI_API_KEY=your_key python3 analyze_log.py build_log.txt

REQUIREMENTS:
    - Python 3.8 or higher
    - google-generativeai package (install: pip install google-generativeai)
    - Valid Gemini API key

OUTPUT:
    The analysis will be displayed in the console and saved to the output file.
    The file contains:
    - Root cause of failure
    - Exact error location
    - Step-by-step fix recommendations
    - Prevention tips
    - Additional resources

For more information, visit:
    https://github.com/rishalgawade/ai-log-analyzer
"""
    print(help_text)


def main():
    """Main execution flow"""

    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        display_help()
        sys.exit(0)

    # Header
    print("\n" + "=" * 80)
    print("🔍 JENKINS BUILD LOG ANALYZER")
    print("=" * 80 + "\n")

    # Validate arguments
    if len(sys.argv) < 2:
        print("❌ Error: Missing required argument\n")
        print("Usage: python3 analyze_log.py <log_file> [output_file]\n")
        print("Examples:")
        print("  python3 analyze_log.py build_log.txt")
        print("  python3 analyze_log.py build_log.txt analysis.txt\n")
        print("For more help, run: python3 analyze_log.py --help\n")
        sys.exit(1)

    log_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "analysis.txt"

    # Display configuration
    print("📋 Configuration:")
    print(f"   Input Log:  {log_file}")
    print(f"   Output File: {output_file}")
    print()

    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set!")
        print("   Get your API key from: https://aistudio.google.com/app/apikey")
        print("   Set it with: export GEMINI_API_KEY='your_key_here'")
        print()

    # Step 1: Read the log file
    print("📄 Step 1/4: Reading build log...")
    log_content = read_log_file(log_file)
    log_size = len(log_content)
    print(f"✅ Log file read successfully")
    print(f"   Size: {log_size:,} characters ({log_size / 1024:.2f} KB)")
    print()

    # Step 2: Analyze with Gemini AI
    print("🤖 Step 2/4: Analyzing with Gemini AI...")
    print("   This may take 10-30 seconds...")
    analysis = analyze_with_gemini(log_content)
    print("✅ AI analysis completed")
    print()

    # Step 3: Save analysis to file
    print("💾 Step 3/4: Saving analysis...")
    save_success = save_analysis(analysis, output_file)
    print()

    # Step 4: Display analysis in console
    print("📊 Step 4/4: Displaying results")
    print("=" * 80)
    print("AI ANALYSIS RESULTS")
    print("=" * 80 + "\n")
    print(analysis)
    print("\n" + "=" * 80)

    # Summary
    print("\n✅ Analysis Complete!")
    if save_success:
        print(f"   📁 Full report saved to: {output_file}")
    print(f"   📏 Original log size: {log_size:,} characters")
    print(f"   🤖 AI model used: Gemini 2.0 Flash")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()