import os
import re

def split_sentences(text):
    # Split text into complete sentences
    return re.split(r'(?<=[.!?])\s+', text.strip())

def chunk_sentences(sentences, max_length):
    chunks = []
    current = ''

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_length:
            current += sentence + ' '
        else:
            chunks.append(current.strip())
            current = sentence + ' '

    if current:
        chunks.append(current.strip())

    return chunks

def process_file(input_path, output_dir, max_length):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by '•', treat each part after '•' as a new chapter
    parts = content.split('•')
    os.makedirs(output_dir, exist_ok=True)
    
    file_id = 1
    for i in range(1, len(parts)):
        # Restore the lost bullet and trim
        chapter = '•' + parts[i].strip()
        sentences = split_sentences(chapter)
        chunks = chunk_sentences(sentences, max_length)

        for chunk in chunks:
            filename = os.path.join(output_dir, f'chunk_{file_id:03d}.txt')
            with open(filename, 'w', encoding='utf-8') as f_out:
                f_out.write(chunk)
            print(f"Wrote {filename}")
            file_id += 1

# Example usage
process_file('/Users/stepankulakov/Desktop/diploma/world_war_one/original_text_clean.txt', 'output_chunks', max_length=5000)
