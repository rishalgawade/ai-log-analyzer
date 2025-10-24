#!/usr/bin/env python3
"""
Enhanced Jenkins Build Log Analyzer with GitHub PR Commenting
Analyzes build failures using Google Gemini AI and posts results to GitHub PRs
"""

import os
import sys
import google.generativeai as genai
from github import Github
from datetime import datetime


def read_log_file(log_path):
    """Read the Jenkins build log file"""
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
    """Analyze build log using Gemini AI"""
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        return "❌ Error: GEMINI_API_KEY environment variable not set"

    # Truncate if too long (keep the end where errors usually are)
    if len(log_content) > max_chars:
        print(f"⚠️  Log truncated from {len(log_content)} to {max_chars} characters")
        log_content = "...[earlier output truncated]...\n\n" + log_content[-max_chars:]

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        prompt = f"""
You are an expert DevOps engineer analyzing a Jenkins CI/CD build failure.

Analyze this build log and provide a comprehensive but concise analysis:

## 🔍 Root Cause
Identify the PRIMARY reason for the build failure (1-2 sentences)

## 📍 Error Location
Point to the specific file, line number, or command that failed

## 🔧 Recommended Fixes
Provide 3-5 ACTIONABLE steps to resolve this issue:
1. [First step with specific command or action]
2. [Second step]
3. [etc.]

## 💡 Prevention Tips
Suggest 2-3 best practices to prevent this issue in the future

## 🔗 Relevant Documentation
If applicable, mention relevant documentation or resources

Build Log:
---
{log_content}
---

Format your response in clear Markdown suitable for a GitHub comment.
Be technical but accessible. Focus on actionable insights.
"""

        print("🤖 Analyzing build log with Gemini AI...")
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        error_msg = f"""
❌ **Error during AI analysis**
```
{str(e)}
```

**Possible causes:**
- API key invalid or expired
- Network connectivity issues
- API rate limit exceeded
- Model unavailable

**Please check:**
1. Verify GEMINI_API_KEY is set correctly
2. Check network connectivity
3. Visit https://aistudio.google.com to verify API status
"""
        return error_msg


def post_github_comment(repo_name, pr_number, comment_body):
    """Post AI analysis as a comment on the GitHub PR"""
    github_token = os.getenv('GITHUB_TOKEN')

    if not github_token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        return False

    try:
        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        # Create comment
        comment = pr.create_issue_comment(comment_body)

        print(f"✅ Comment posted successfully to PR #{pr_number}")
        print(f"   PR URL: {pr.html_url}")
        print(f"   Comment URL: {comment.html_url}")
        return True

    except Exception as e:
        print(f"❌ Error posting GitHub comment: {e}")
        print(f"   Repository: {repo_name}")
        print(f"   PR Number: {pr_number}")
        return False


def save_analysis(analysis_text, output_path):
    """Save the AI analysis to a file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("🤖 AI-POWERED BUILD FAILURE ANALYSIS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(analysis_text)
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("Analysis completed by Jenkins AI Log Analyzer\n")
            f.write("Powered by Google Gemini AI\n")
            f.write("=" * 80 + "\n")

        print(f"✅ Analysis saved to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving analysis: {e}")
        return False


def main():
    """Main execution flow"""

    print("\n" + "=" * 80)
    print("🚀 JENKINS AI LOG ANALYZER WITH GITHUB INTEGRATION")
    print("=" * 80 + "\n")

    # Parse command line arguments
    if len(sys.argv) < 4:
        print("❌ Insufficient arguments\n")
        print("Usage:")
        print("  python3 analyze_and_comment.py <log_file> <repo_name> <pr_number> [output_file]\n")
        print("Arguments:")
        print("  log_file    : Path to Jenkins build log (e.g., build_log.txt)")
        print("  repo_name   : GitHub repository in format 'owner/repo'")
        print("  pr_number   : Pull request number")
        print("  output_file : (Optional) Path for analysis output (default: analysis.txt)\n")
        print("Example:")
        print("  python3 analyze_and_comment.py build_log.txt rishalgawade/jenkins-ai-log-analyzer 5\n")
        sys.exit(1)

    log_file = sys.argv[1]
    repo_name = sys.argv[2]
    pr_number = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else "analysis.txt"

    # Validate inputs
    if '/' not in repo_name:
        print(f"❌ Error: Invalid repository name '{repo_name}'")
        print("   Expected format: 'owner/repo' (e.g., 'rishalgawade/jenkins-ai-log-analyzer')")
        sys.exit(1)

    if not pr_number.isdigit():
        print(f"❌ Error: Invalid PR number '{pr_number}'")
        print("   PR number must be a positive integer")
        sys.exit(1)

    # Display configuration
    print("📋 Configuration:")
    print(f"   Log File: {log_file}")
    print(f"   Repository: {repo_name}")
    print(f"   PR Number: #{pr_number}")
    print(f"   Output File: {output_file}")
    print()

    # Step 1: Read build log
    print("📄 Step 1: Reading build log...")
    log_content = read_log_file(log_file)
    print(f"✅ Log file read successfully ({len(log_content):,} characters)")
    print()

    # Step 2: Analyze with AI
    print("🤖 Step 2: Analyzing with Gemini AI...")
    analysis = analyze_with_gemini(log_content)
    print("✅ AI analysis completed")
    print()

    # Step 3: Save analysis locally
    print("💾 Step 3: Saving analysis...")
    save_analysis(analysis, output_file)
    print()

    # Step 4: Post to GitHub PR
    print(f"📝 Step 4: Posting comment to GitHub PR #{pr_number}...")

    # Format comment with header and footer
    comment_body = f"""## 🤖 AI Build Failure Analysis

{analysis}

---
<sub>🔬 Analysis powered by **Google Gemini AI** | 🤖 Generated by **Jenkins AI Log Analyzer**</sub>
<sub>⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</sub>
"""

    success = post_github_comment(repo_name, pr_number, comment_body)
    print()

    # Step 5: Display summary
    print("=" * 80)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    print(analysis)
    print()
    print("=" * 80)

    if success:
        print("✅ All operations completed successfully!")
        print(f"   View the analysis on GitHub: https://github.com/{repo_name}/pull/{pr_number}")
    else:
        print("⚠️  Analysis completed but GitHub comment failed")
        print(f"   Check the saved file: {output_file}")

    print("=" * 80)
    print()


if __name__ == "__main__":
    main()