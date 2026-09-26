import os
import re
import ast
import subprocess
import ollama

SKILLS_DIR = "skills"
os.makedirs(SKILLS_DIR, exist_ok=True)

class SkillForge:
    """NOKE's Autonomous Engineering Workshop — writes, tests, and runs its own code."""

    @staticmethod
    def create_tool(task_description: str) -> str:
        """Asks Llama to write a Python script, checks syntax, and saves it."""
        print(f"\n [NOKE Forge]: Engineering script for: '{task_description}'...")

        prompt = f"""You are an elite Python developer AI.
Write a clean, standalone, executable Python script to do the following task:
"{task_description}"

STRICT RULES:
1. Output ONLY pure Python code.
2. Do NOT write any conversational explanation, introduction, or markdown chatter.
3. Keep the script self-contained and print its final result clearly to stdout using print().
4. Use standard libraries or popular libraries like requests, json, math, datetime, os.
"""

        try:
            response = ollama.chat(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": prompt}]
            )
            raw_code = response['message']['content'].strip()

            # Clean out any markdown backticks if Llama wrapped it in ```python ... ```
            cleaned_code = re.sub(r"^```(?:python)?\s*", "", raw_code, flags=re.IGNORECASE)
            cleaned_code = re.sub(r"\s*```$", "", cleaned_code)

            # Safety check: Verify syntax before saving
            try:
                ast.parse(cleaned_code)
            except SyntaxError as e:
                return f"My generated code had a syntax anomaly on line {e.lineno}. Refusing to save broken code."

            # Generate a clean file name
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '', task_description.lower().replace(" ", "_"))[:20]
            if not safe_name:
                safe_name = "custom_tool"
            filename = os.path.join(SKILLS_DIR, f"{safe_name}.py")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(cleaned_code)

            print(f" [Code Created]: Saved to {filename}")
            return f"I have engineered the script {safe_name}.py in the skills folder, Able. The tool is ready for deployment."

        except Exception as e:
            return f"Engineering failed due to an internal error: {e}"

    @staticmethod
    def run_tool(tool_name: str) -> str:
        """Executes a previously created skill and speaks the result."""
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', tool_name.lower().replace(".py", "").replace(" ", "_"))
        target_path = os.path.join(SKILLS_DIR, f"{clean_name}.py")

        if not os.path.exists(target_path):
            # Check if any file contains the name
            matching = [f for f in os.listdir(SKILLS_DIR) if clean_name in f]
            if matching:
                target_path = os.path.join(SKILLS_DIR, matching[0])
            else:
                return f"I cannot find a skill named {tool_name} in my workshop, Able."

        print(f" [NOKE Forge]: Executing {target_path}...")
        try:
            result = subprocess.run(
                ["python", target_path],
                capture_output=True,
                text=True,
                timeout=20
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                return f"Script execution complete. Result: {output if output else 'Success with no output.'}"
            else:
                err = result.stderr.strip()[:100]
                return f"The tool ran into an execution error: {err}"
        except subprocess.TimeoutExpired:
            return "Execution timed out. Terminated the process for safety."
        except Exception as e:
            return f"Failed to execute tool: {e}"