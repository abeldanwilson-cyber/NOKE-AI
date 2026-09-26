import os
import re
import ast
import subprocess
import requests
import ollama
from bs4 import BeautifulSoup

SKILLS_DIR = "skills"
os.makedirs(SKILLS_DIR, exist_ok=True)

# ── Optional DuckDuckGo search ──────────────────
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

class SelfSolver:
    """
    NOKE's autonomous problem-solving engine.
    When NOKE receives an unknown command, this module:
      1. Searches the internet for how to solve it in Python
      2. Asks Llama to write a clean Python solution
      3. Verifies the syntax
      4. Runs it and returns the real output
    """

    # ──────────────────────────────────────────
    #  STEP 1: Research the solution online
    # ──────────────────────────────────────────
    @staticmethod
    def _research_solution(task: str) -> str:
        query = f"Python code to {task} step by step"
        print(f"   [Resolver] Researching: {query}")
        try:
            if DDGS:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=4))
                if results:
                    return "\n\n".join(
                        f"Source: {r['title']}\nInfo: {r['body']}" for r in results
                    )
            # Fallback: direct web search
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(
                f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}",
                headers=headers, timeout=8
            )
            soup = BeautifulSoup(r.text, "html.parser")
            snippets = [s.get_text(strip=True) for s in soup.select(".result__snippet")][:4]
            return "\n".join(snippets)
        except Exception as e:
            return f"Could not research online: {e}"

    # ──────────────────────────────────────────
    #  STEP 2: Generate Python code via Llama
    # ──────────────────────────────────────────
    @staticmethod
    def _generate_code(task: str, research_context: str) -> str:
        prompt = f"""You are an elite Python developer.
Your job: Write a complete, self-contained Python script to accomplish this task:

TASK: "{task}"

RESEARCH CONTEXT (use this for guidance):
{research_context[:1500]}

STRICT RULES:
1. Output ONLY pure Python code. No markdown, no backticks, no explanation.
2. The script must run without user input.
3. Use standard libraries OR well-known pip packages (requests, yt-dlp, Pillow, etc.).
4. Print the final result or status clearly using print().
5. Handle errors with try/except and print helpful error messages.
6. If the task involves downloading, save to a folder called "noke_downloads".
7. Keep it concise — do not over-engineer.
"""
        try:
            response = ollama.chat(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response['message']['content'].strip()
            # Strip markdown code fences if present
            raw = re.sub(r"^```(?:python)?\s*", "", raw, flags=re.IGNORECASE | re.MULTILINE)
            raw = re.sub(r"\s*```\s*$", "", raw, flags=re.MULTILINE)
            return raw.strip()
        except Exception as e:
            return f"# Code generation failed: {e}"

    # ──────────────────────────────────────────
    #  STEP 3: Validate Python syntax
    # ──────────────────────────────────────────
    @staticmethod
    def _validate_code(code: str) -> tuple:
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error on line {e.lineno}: {e.msg}"

    # ──────────────────────────────────────────
    #  STEP 4: Save and run the code
    # ──────────────────────────────────────────
    @staticmethod
    def _save_and_run(task: str, code: str) -> str:
        # Create a clean filename from the task description
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', task.lower())[:30].strip('_')
        if not safe_name:
            safe_name = "auto_task"
        filepath = os.path.join(SKILLS_DIR, f"{safe_name}.py")

        # Save the generated code
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"   [Resolver] Running: {filepath}")

        # Execute and capture output
        try:
            result = subprocess.run(
                ["python", filepath],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if result.returncode == 0 and stdout:
                # Truncate very long outputs for speech
                if len(stdout) > 300:
                    return stdout[:300] + "... result truncated."
                return stdout

            elif result.returncode == 0:
                return "Task completed successfully, Sir. No output was produced."

            else:
                # Give a clean error summary
                error_summary = stderr.split('\n')[-1] if stderr else "Unknown error"
                return f"Task ran but encountered an error: {error_summary}"

        except subprocess.TimeoutExpired:
            return "Task timed out after 60 seconds, Sir. It may still be running in the background."
        except Exception as e:
            return f"Execution failed, Sir: {e}"

    # ──────────────────────────────────────────
    #  MAIN PUBLIC METHOD
    # ──────────────────────────────────────────
    @staticmethod
    def solve(task: str) -> str:
        """
        Full pipeline: research -> generate code -> validate -> run -> return result.
        Called by noke.py when no built-in handler exists for a task.
        """
        print(f"\n   [Self-Solver] Activating autonomous problem solver...")
        print(f"   [Self-Solver] Task: {task}")

        # Step 1: Research
        print("   [Self-Solver] Step 1/4: Researching solution online...")
        context = SelfSolver._research_solution(task)

        # Step 2: Generate code
        print("   [Self-Solver] Step 2/4: Engineering Python solution...")
        code = SelfSolver._generate_code(task, context)

        if code.startswith("# Code generation failed"):
            return f"I was unable to engineer a solution for that task, Sir. {code}"

        # Step 3: Validate
        print("   [Self-Solver] Step 3/4: Validating code syntax...")
        valid, error = SelfSolver._validate_code(code)
        if not valid:
            # Try once more with error feedback
            print(f"   [Self-Solver] Syntax issue detected. Regenerating...")
            fix_prompt = f"Fix this Python code. The error is: {error}\n\nCode:\n{code}\n\nReturn ONLY the corrected Python code."
            try:
                fix_response = ollama.chat(
                    model="llama3.2:3b",
                    messages=[{"role": "user", "content": fix_prompt}]
                )
                code = fix_response['message']['content'].strip()
                code = re.sub(r"^```(?:python)?\s*", "", code, flags=re.IGNORECASE | re.MULTILINE)
                code = re.sub(r"\s*```\s*$", "", code, flags=re.MULTILINE)
                valid, error = SelfSolver._validate_code(code)
                if not valid:
                    return f"I generated a solution but the code has a syntax issue I could not resolve, Sir: {error}"
            except Exception as e:
                return f"Code generation and fix both failed, Sir: {e}"

        # Step 4: Run
        print("   [Self-Solver] Step 4/4: Executing solution...")
        result = SelfSolver._save_and_run(task, code)

        return result

    # ──────────────────────────────────────────
    #  DETECT IF A QUERY IS AN ACTIONABLE TASK
    # ──────────────────────────────────────────
    @staticmethod
    def is_actionable_task(query: str) -> bool:
        """
        Returns True if the query sounds like something NOKE should DO,
        not just answer or explain.
        """
        q = query.lower()
        action_verbs = [
            "download", "convert", "compress", "resize", "rename",
            "merge", "split", "extract", "install", "create", "generate",
            "send", "upload", "backup", "copy", "move", "delete",
            "scrape", "fetch", "get me", "find me", "save", "record",
            "automate", "schedule", "monitor", "track", "translate",
            "encrypt", "decrypt", "zip", "unzip"
        ]
        return any(verb in q for verb in action_verbs)
