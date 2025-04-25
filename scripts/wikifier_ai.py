import os
from openai import OpenAI
import wikifier

client = OpenAI(api_key="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") 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "output_chunks")
OUTPUT_FILE = os.path.join(BASE_DIR, "result", "wikifier_output.txt")
PROMPT_FILE = os.path.join(BASE_DIR, "prompt", "wikifier_prompt.txt")

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def load_prompt_template():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def extract_triples(text, model="gpt-4o"):
    types = wikifier.extract_types_from_text(text)
    template = load_prompt_template()

    types_text = "\n".join(
        f"{entity}: " + ", ".join(classes) for entity, classes in types.items()
    )
    ontology_prompt = (
        template
        .replace("<<<TEXT>>>", text.strip())
        .replace("<<<TYPES>>>", types_text)
    )
    print(ontology_prompt)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a knowledge extraction assistant"},
                {"role": "user", "content": ontology_prompt}
            ],
            temperature=0
        )
        return types_text + '\n' + '\n' + 'LLM best matches\n' + response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ API error: {e}")
        return ""


def main():
    txt_files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".txt"))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for filename in txt_files:
            input_path = os.path.join(INPUT_DIR, filename)
            print(f"📄 Processing {filename}...")

            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()
             
            result = extract_triples(text)
            out.write(f"# Entities from {filename}\n")
            out.write(result + "\n\n")
    print(f"\n✅ All entities written to one file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
