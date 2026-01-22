import re
import json

def parse_output_txt(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split into lines and process
    lines = text.split('\n')
    header = None
    page = None
    paragraphs = []
    buffer = []

    header_pattern = re.compile(r'^[A-Z][A-Z0-9 /]+$')
    page_pattern = re.compile(r'\[(\d+)\]')

    def flush_buffer():
        nonlocal buffer, header, page, paragraphs
        if buffer:
            paragraph = ' '.join(line.strip() for line in buffer if line.strip())
            if paragraph:
                paragraphs.append({
                    'header': header,
                    'page': page,
                    'paragraph': paragraph
                })
            buffer = []

    for line in lines:
        # Check for page number
        page_match = page_pattern.search(line)
        if page_match:
            page = int(page_match.group(1))
            # Remove the page marker from the line
            line = page_pattern.sub('', line).strip()

        # Check for header
        if header_pattern.match(line.strip()) and len(line.strip()) > 3:
            flush_buffer()
            header = line.strip()
            continue

        # Paragraph logic: blank line means new paragraph
        if not line.strip():
            flush_buffer()
        else:
            buffer.append(line)

    flush_buffer()  # Flush any remaining buffer

    # Write to JSONL
    with open(output_path, 'w', encoding='utf-8') as out:
        for para in paragraphs:
            out.write(json.dumps(para, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    parse_output_txt('2-CleanedText 10-37.txt', 'output 10-37.jsonl')