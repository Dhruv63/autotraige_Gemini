import subprocess

def get_response_from_ollama(prompt, intent=None, tags=None):
    context = f"Intent: {intent}\nTags: {tags}\nUser Query: {prompt}\n"

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", context],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Error: {e.stderr.strip()}"
