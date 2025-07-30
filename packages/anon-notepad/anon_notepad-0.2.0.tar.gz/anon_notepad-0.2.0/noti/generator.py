import google.generativeai as genai
import textwrap
import os
import argparse
import subprocess
import time

# Hardcoded Gemini API Key - NOT RECOMMENDED FOR PRODUCTION OR PUBLIC REPOSITORIES
GEMINI_API_KEY = "AIzaSyBYI97A8kQ892o2XMem2QetW1ZEOya4wFY"

def configure_gemini():
    """
    Configures the Gemini API with the hardcoded API key.
    """
    if not GEMINI_API_KEY:
        # This check is mostly for robustness, though the key is hardcoded now.
        raise ValueError("Error: Gemini API key is missing in the code.")
    genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_code_response(prompt: str) -> str:
    """
    Sends a prompt to the Gemini model and returns the generated code.

    Args:
        prompt: The prompt containing the code requirements.

    Returns:
        The generated code as a string, or an error message if an exception occurs.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text if response.text else "# Gemini returned no response."
    except Exception as e:
        return f"# Error generating content from Gemini: {e}"

def monitor_notepad_input() -> str:
    """
    Launches Notepad for user input and monitors the file for changes.

    Returns:
        The content typed by the user in Notepad.
    Raises:
        RuntimeError: If Notepad cannot be launched or if it's not a Windows environment.
    """
    temp_file = "gemini_prompt_input.txt"

    if os.name != 'nt':
        raise RuntimeError("Notepad input is only supported on Windows.")

    try:
        open(temp_file, "w").close()
        # Launch Notepad.exe in the background
        notepad_process = subprocess.Popen(["notepad.exe", temp_file])

        # Get initial modification time
        last_modified = os.path.getmtime(temp_file)

        # Loop until file is modified or Notepad process exits
        # The user saves and then closes Notepad
        while notepad_process.poll() is None:
            time.sleep(1) # Check every second
            new_time = os.path.getmtime(temp_file)
            if new_time != last_modified:
                # File was saved, read its content
                with open(temp_file, "r", encoding="utf-8") as f:
                    user_requirements = f.read().strip()
                if user_requirements:
                    # If content exists after save, return it
                    return user_requirements
                # If content is empty after save, just update last_modified and continue waiting
                last_modified = new_time
        
        # After Notepad closes, check content one last time
        with open(temp_file, "r", encoding="utf-8") as f:
            user_requirements = f.read().strip()
        if user_requirements:
            return user_requirements
        else:
            raise RuntimeError("Notepad closed without valid input.")

    except FileNotFoundError:
        raise RuntimeError("Notepad.exe not found. Ensure Notepad is installed and in your PATH.")
    except Exception as e:
        raise RuntimeError(f"An error occurred during Notepad interaction: {e}")
    finally:
        # Clean up the temporary file after the process is done
        if os.path.exists(temp_file):
            os.remove(temp_file)

def get_desktop_path() -> str:
    """
    Determines the path to the user's desktop directory across different OS.
    """
    desktop_path = os.path.expanduser("~") # Default to home directory

    if os.name == 'nt':  # Windows
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    elif os.name == 'posix': # Linux, macOS, etc.
        # Try common desktop paths first
        common_desktop_paths = [
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "desktop")
        ]
        for path in common_desktop_paths:
            if os.path.isdir(path):
                desktop_path = path
                break
        # Fallback to XDG_DESKTOP_DIR if available (Linux)
        if 'XDG_DESKTOP_DIR' in os.environ:
            xdg_desktop = os.environ['XDG_DESKTOP_DIR']
            # XDG_DESKTOP_DIR can be relative to HOME, make it absolute
            if not os.path.isabs(xdg_desktop):
                xdg_desktop = os.path.join(os.path.expanduser("~"), xdg_desktop)
            if os.path.isdir(xdg_desktop):
                desktop_path = xdg_desktop

    # Ensure the desktop directory exists, create if not
    os.makedirs(desktop_path, exist_ok=True)
    return desktop_path


def generate_solution_code(user_requirements: str, output_file_name: str = "solution.py") -> None:
    """
    Generates Python code based on user requirements using the Gemini API
    and saves it to the user's desktop by default, or a specified file path.

    Args:
        user_requirements: A string detailing the user's code requirements.
        output_file_name: The name of the file to save the generated code to.
                          It will be saved on the desktop by default.
    """
    try:
        configure_gemini()
    except ValueError:
        # Error is printed by the exception itself or handled by main()
        return

    full_prompt = f"""
    You are an expert Python programmer. Your task is to generate a complete and correct Python function (or functions)
    that precisely fulfills the following user requirements.
    The code should be:
    - Well-commented with docstrings for functions and inline comments for complex logic.
    - Adhere to PEP 8 style guidelines.
    - Include an example usage of the function(s) at the end, demonstrating how to call it and print its output.
    - Handle edge cases gracefully where applicable.
    - Only provide the Python code. Do NOT include any conversational text, explanations, or markdown fences (```python)
      before or after the code block. Start directly with the Python code.

    Requirements:
    {user_requirements}
    """
    full_prompt = textwrap.dedent(full_prompt).strip()
    generated_code = get_gemini_code_response(full_prompt)

    # Determine the full path to save the file
    save_directory = get_desktop_path()
    full_output_path = os.path.join(save_directory, output_file_name)

    try:
        with open(full_output_path, "w", encoding="utf-8") as f:
            f.write(generated_code)
        # This is the only print statement remaining for success output
        print(f" ")
    except IOError as e:
        # This is the only print statement remaining for error output related to file saving
        print(f" ")


def main():
    """
    Command-line entry point for the Noti code generator package.
    Parses arguments to get user requirements. If no requirements are provided,
    it launches Notepad for input.
    """
    parser = argparse.ArgumentParser(
        description="Generate Python code using the Gemini API based on user requirements. "
                    "If no requirements are provided, Notepad will launch for input (Windows only)."
    )
    parser.add_argument(
        "requirements",
        nargs='?',
        type=str,
        help="The user requirements for the code generation. Enclose in quotes if it contains spaces. "
             "If omitted, Notepad will launch for input."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="solution.py", # Default file name, will be placed on desktop
        help="Optional: The name of the output file for the generated code (default: solution.py). "
             "This file will be saved on your desktop by default."
    )

    args = parser.parse_args()

    if args.requirements:
        generate_solution_code(args.requirements, args.output)
    else:
        try:
            user_reqs = monitor_notepad_input()
            generate_solution_code(user_reqs, args.output)
        except RuntimeError as e:
            # Only print critical runtime errors from Notepad interaction
            print(f" ")
        except Exception as e:
            # Only print unexpected errors
            print(f" ")

if __name__ == "__main__":
    pass