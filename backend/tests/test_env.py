import os
from dotenv import load_dotenv

print("=== Env Diagnostics ===")
print("Current Working Directory:", os.getcwd())
print("Does .env exist in CWD?", os.path.exists(".env"))

if os.path.exists(".env"):
    print("Reading .env contents (lines):")
    with open(".env", "r") as f:
        for line in f:
            if line.strip():
                print("  ", line.strip().split('=')[0] + " = " + ("*" * 10 if '=' in line else ""))
else:
    print("Looking for .env file in parent folders...")
    # Scan up
    path = os.getcwd()
    for _ in range(3):
        path = os.path.dirname(path)
        env_path = os.path.join(path, ".env")
        if os.path.exists(env_path):
            print(f"Found .env in: {env_path}")
            break

print("\nRunning load_dotenv()...")
load_dotenv()

key = os.getenv("OPENAI_API_KEY")
if key:
    print(f"Success! Loaded key length: {len(key)}")
    print(f"Starts with: {key[:12]}")
    print(f"Is placeholder? {key == 'your_openai_api_key_here'}")
else:
    print("Error: OPENAI_API_KEY is not set in environment.")
print("=======================")
