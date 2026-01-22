
import os
import ollama
import math

# === USER CONFIGURABLE PARAMETERS ===
# Edit these variables in the editor before running
TXT_FILE = 'output3.txt'  # Path to TXT file to clean
OLLAMA_MODEL = 'llama3'   # Ollama model to use
# Prompt instructs the model to ONLY output the cleaned text, with no extra explanation or formatting
CLEAN_PROMPT = (
    'Clean up the following text for clarity and formatting. Remove any OCR errors, fix paragraph breaks, and ensure the text is readable. Output ONLY the cleaned text, with no extra explanation, commentary, or formatting. Do not alter the structure of the text, or the content of the text, unless obviously disrupted by OCR.'
)
CHUNK_SIZE = 1500         # Chunk size in characters
OUTPUT_FILE = "2-CleanedText 10-37.txt"        # Output file for cleaned text, or None to print
# Toggle: if True, chunk by page (using page numbers as identifiers); if False, use improved paragraph/table chunking
CHUNK_BY_PAGE = True
# Toggle: if True, review each chunk before sending to Ollama
DEBUG_REVIEW_CHUNKS = True


# ====================================


import re

def chunk_text(text, chunk_size=1500, by_page=False):
    """
    Split text into chunks. If by_page is True, split by detected page numbers (e.g., [10]),
    otherwise split by improved paragraph/table detection and chunk size.
    """
    if by_page:
        # Split by lines that are exactly a page number in brackets (e.g., [10])
        lines = text.split('\n')
        pages = []
        current = []
        page_number_pattern = re.compile(r'^\[\d+\]$')
        for line in lines:
            if page_number_pattern.match(line.strip()):
                if current:
                    pages.append('\n'.join(current).strip())
                    current = []
            else:
                current.append(line)
        if current:
            pages.append('\n'.join(current).strip())
        return [p for p in pages if p.strip()]
    else:
        # Improved paragraph/table detection
        lines = text.split('\n')
        chunks = []
        current = []
        current_len = 0
        in_table = False
        for i, line in enumerate(lines):
            # Detect table start/end by looking for lines with lots of | or + or table-like structure
            is_table_line = bool(re.match(r'^[ \t]*[+|].*[+|][ \t]*$', line)) or (line.count('|') >= 2)
            if is_table_line:
                if not in_table and current:
                    # Flush current paragraph chunk before starting table
                    chunks.append('\n'.join(current))
                    current = []
                    current_len = 0
                in_table = True
                current.append(line)
                current_len += len(line) + 1
                # If next line is not a table, flush table chunk
                if i+1 == len(lines) or not (bool(re.match(r'^[ \t]*[+|].*[+|][ \t]*$', lines[i+1])) or (lines[i+1].count('|') >= 2)):
                    chunks.append('\n'.join(current))
                    current = []
                    current_len = 0
                    in_table = False
            elif line.strip() == '':
                if current:
                    chunks.append('\n'.join(current))
                    current = []
                    current_len = 0
                in_table = False
            else:
                current.append(line)
                current_len += len(line) + 1
                if current_len > chunk_size and current:
                    chunks.append('\n'.join(current))
                    current = []
                    current_len = 0
        if current:
            chunks.append('\n'.join(current))
        return [c for c in chunks if c.strip()]

def clean_chunk(chunk, model, prompt):
    """Send a chunk to Ollama for cleaning using the given prompt."""
    full_prompt = f"{prompt}\n\nText:\n{chunk}\n\nCleaned Text:"
    response = ollama.chat(model=model, messages=[{"role": "user", "content": full_prompt}])
    return response['message']['content']

def main():
    if not os.path.exists(TXT_FILE):
        print(f"File not found: {TXT_FILE}")
        return
    with open(TXT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    chunks = chunk_text(text, chunk_size=CHUNK_SIZE, by_page=CHUNK_BY_PAGE)
    print(f"Chunking complete: {len(chunks)} chunks.")
    cleaned_chunks = []
    for i, chunk in enumerate(chunks):
        if DEBUG_REVIEW_CHUNKS:
            print(f"\n---\nChunk {i+1}/{len(chunks)}:\n{'-'*40}\n{chunk}\n{'-'*40}")
            action = input("[Enter] to continue, [s] to skip, [e] to edit: ").strip().lower()
            if action == 's':
                print("Skipping this chunk.")
                continue
            elif action == 'e':
                print("Enter new chunk text (end with a blank line):")
                new_lines = []
                while True:
                    line = input()
                    if line == '':
                        break
                    new_lines.append(line)
                chunk = '\n'.join(new_lines)
        print(f"Cleaning chunk {i+1}/{len(chunks)}...")
        cleaned = clean_chunk(chunk, OLLAMA_MODEL, CLEAN_PROMPT)
        cleaned_chunks.append(cleaned)
    cleaned_text = '\n\n'.join(cleaned_chunks)
    if OUTPUT_FILE:
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
                out.write(cleaned_text)
            print(f"Cleaned text written to {OUTPUT_FILE}")
        except Exception as e:
            print(f"Failed to write to {OUTPUT_FILE}: {e}")
    else:
        print("\n---\nCleaned Text:\n")
        print(cleaned_text)

# --- Debugging Model Hallucination ---
# If the model outputs random/unrelated results, possible causes include:
# - The chunk contains non-source text, artifacts, or ambiguous formatting
# - The prompt is too vague or not restrictive enough
# - The chunk is too short or too long, causing context confusion
# - Ollama model is not well-aligned for cleaning tasks (try a different model)
# Use DEBUG_REVIEW_CHUNKS = True to inspect and edit chunks before sending to Ollama.

if __name__ == '__main__':
    main()
