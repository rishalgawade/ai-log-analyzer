#!/usr/bin/env python3
import os, sys, json, requests, textwrap

def read_log(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def make_prompt(log_text):
    log_tail = "\n".join(log_text.splitlines()[-2000:])
    prompt = textwrap.dedent(f"""
      You are an assistant that analyzes CI build logs. Provide:
      1) Short summary
      2) Most likely root cause(s)
      3) Next debugging steps
      4) Suggested fix
      ========= LOG START =========
      {log_tail}
      ========= LOG END =========
    """)
    return prompt

def call_gemini(prompt, api_key, model="gemini-1.5-flash-latest"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {"contents":[{"parts":[{"text": prompt}]}], "temperature":0.0}
    resp = requests.post(url, params={"key": api_key}, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if "candidates" in data:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    return json.dumps(data, indent=2)

def main():
    if len(sys.argv) < 2:
        print("usage: analyze_log.py <logfile> [outfile]")
        sys.exit(1)
    log_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "analysis.txt"
    log = read_log(log_path)
    prompt = make_prompt(log)
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        print("ERROR: AI_API_KEY not set")
        sys.exit(1)
    try:
        analysis = call_gemini(prompt, api_key)
    except Exception as e:
        analysis = f"ERROR calling Gemini API: {e}"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(analysis)
    print(analysis)

if __name__ == "__main__":
    main()
