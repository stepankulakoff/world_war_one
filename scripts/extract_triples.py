import os
from openai import OpenAI


client = OpenAI(api_key="") 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "output_chunks")
OUTPUT_FILE = os.path.join(BASE_DIR, "result", "4o_prompt_one_output.txt")
PROMPT_FILE = os.path.join(BASE_DIR, "prompt", "prompt_one.txt")

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def load_prompt_template():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def extract_triples(text, model="gpt-4o"):
    ontology_prompt = load_prompt_template().replace("<<<TEXT>>>", text.strip())

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a knowledge graph extraction assistant using a predefined ontology."},
                {"role": "user", "content": ontology_prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
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

            triples = extract_triples(text)
            out.write(f"# Triples from {filename}\n")
            out.write(triples + "\n\n")

    print(f"\n✅ All triples written to one file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
