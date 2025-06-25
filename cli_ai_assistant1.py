import os
import json
import traceback
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

load_dotenv()

# ✅ List of Available Golden Path Templates
GOLDEN_PATH_TEMPLATES = [
    {
        "name": "Golden Path Microservice (Flask, Python)",
        "stack": ["python", "flask"],
        "framework": "Flask",
        "docker": True,
        "observability": ["Prometheus", "Grafana"],
        "test_frameworks": ["pytest"],
        "repo_url": "https://github.com/ramannkhanna2/cookiecutter-golden-path.git"
    }
]

# 🧠 Prompt for Stack Detection
STACK_DETECT_PROMPT = PromptTemplate(
    input_variables=["project_description"],
    template="""
Extract the technology stack from this project description.
Respond ONLY in this JSON format:

{{
  "stack": ["<tech1>", "<tech2>", ...]
}}

Project Description: {project_description}
"""
)

# 🔍 Match stack with available templates
def find_matching_template(detected_stack):
    for template in GOLDEN_PATH_TEMPLATES:
        if any(tech.lower() in detected_stack for tech in template["stack"]):
            return template
    return None

# 🏗️ Generate fallback scaffold JSON
def fallback_scaffold(detected_stack):
    stack_label = ", ".join(detected_stack)
    return {
        "error": "❌ No matching template found for the given stack.",
        "suggestion": "You can create a new Cookiecutter template for this stack. Here's a sample structure to get you started.",
        "template_scaffold": {
            "cookiecutter.json": {
                "project_name": f"My {stack_label} Microservice",
                "project_slug": f"{'_'.join(detected_stack)}_microservice",
                "author_name": "Your Name",
                "description": f"A simple {stack_label} microservice template with basic observability, Docker, and tests",
                "port": "3000"
            },
            "folder_structure": [
                "{{cookiecutter.project_slug}}/",
                "├── app.main",  # generic
                "├── Dockerfile",
                "├── observability.yaml",
                "├── test/",
                "│   └── app.test"
            ]
        }
    }

def main():
    print("🔧 Developer Template Recommender Assistant\n")
    print("Hugging Face Token Present:", bool(os.getenv("HUGGINGFACEHUB_API_TOKEN")))

    try:
        llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0.3,
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
        )
    except Exception as e:
        print("❌ Error initializing LLM:", e)
        return

    chain = STACK_DETECT_PROMPT | llm

    while True:
        user_input = input("\n📝 Describe your project (or type 'exit'): ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            print("⚠️ Please enter a valid description.")
            continue
        try:
            response = chain.invoke({"project_description": user_input})
            print("\n📦 Raw LLM Output:\n", response)

            try:
                parsed = json.loads(response)
                detected_stack = [s.lower().strip() for s in parsed.get("stack", [])]
                print(f"\n🔍 Detected Stack: {detected_stack}")

                template = find_matching_template(detected_stack)
                if not template:
                    fallback = fallback_scaffold(detected_stack)
                    print(f"\n❌ {fallback['error']}")
                    print(f"\n💡 {fallback['suggestion']}")
                    print("\n📁 Suggested Template Structure:")
                    print(json.dumps(fallback["template_scaffold"], indent=2))
                else:
                    print("\n✅ Recommended Template:\n")
                    for k, v in template.items():
                        print(f"{k}: {v}")
                    confirm = input("\n➡️  Do you want to scaffold this project using the suggested template? (y/n): ").strip().lower()
                    if confirm == 'y':
                        print(f"\n➡️  Scaffolding project using: {template['repo_url']}")
                        os.system(f"cookiecutter {template['repo_url']} --output-dir ./generated-projects")
                        print("\n✅ Project scaffolded successfully into: ./generated-projects")
            except json.JSONDecodeError:
                print("❌ Failed to parse LLM response as JSON. Raw output:")
                print(response)

            print("\n" + "-"*60 + "\n")

        except Exception as e:
            print("Exception traceback:")
            traceback.print_exc()
            print(f"Error message: {e}")

if __name__ == "__main__":
    main()

