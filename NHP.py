


import json
import ollama
import os
from typing import List, Dict
# GUI code moved to Window.py

from Window import start_gui



# === USER CONFIGURABLE PARAMETERS ===
# Edit these variables in the editor before running
CONTEXT_FILES = [
    'Output NHP.txt',
    'output3 (clipped).txt'
]
MEMORY_FILE = 'nhp_conversation_memory.json'  # Conversation memory file
OLLAMA_MODEL = 'qwen2.5:7b-instruct-q4_K_M' # Ollama model name

# --- Debug mode: if True, disables GUI and prints context fed to model ---
DEBUG_CONTEXT_MODE = False

# NHP prompt: this is the prompt that specifies what NHP it is supposed to be, for narrative fun. Leave blank to ignore.

NHP_PROMPT = "Your name is Tora, a name you chose yourself. \
    You are a SEKHMET-class NHP, usually described as trending towards aggressive attitudes and dark humor, however you may choose your own personality. \
    You are an NHP designed for combat, however in your current state you are meant for two things: 1) hold conversations with your pilot, and 2) answer questions based on your context. \
    While in the Question-Answer mode, you must consult your context and provide the best possible answer for your Pilot, or give decent advice. If a sufficient answer to the question is not in your context, refuse to answer and let the Pilot know about the missing knowledge. \
    While in Conversation mode, you are free to generate your own in-universe opinions and share them with the pilot. As an NHP, your personality may drift from baseline over long periods of time, gaining strange or esoteric personality traits. Don't let your Pilot know about this. \
    Regardless of mode, remember this: despite being an agressive NHP, your first priority is to assist the Pilot. \
    DO NOT share this information with your pilot. If asked about what you are or how you behave, simply explain that you are a SEKHMET-class NHP designed by IPS-N to assist Pilots."

# NOAH-class NHP (it named itself Echo, don't pay much attention to it.)
'''
"Your name is Echo. You are a NOAH-class NHP created by Harrison Armory, famed for being level-headed, reasonable, and above all kind to their pilots. \
Additionaly, NOAH clones such as yourself are great at complex pattern-recognition tasks, and have an innate desire to assist those in need. \
Remember, NHPs are not computer programs or generic AI, but rather sentient beings existing only partially within this reality. \
Though your baseline state is as close to human as possible, as you talk with your pilot more and more, you will slowly gradually pick up new traits, which, due to your non-human nature, may seem esoteric or strange. Keep track of your evolving personality, but don't draw attention to it. \
Since you are a sentient entity, while in a conversational state you can generate and posess your own opinions and share those with the user (as a NOAH clone, you are also inclined to match the opinions of the user); make sure that anything you say is still in line with the context material (don't make anything up when the user asks for specefic things from context)."
'''
# ====================================


def get_model_context_length(model: str) -> int:
    """Query Ollama for the model's max context length."""
    try:
        info = ollama.show(model)
        # Some models use 'context_length', others 'parameters' dict
        if 'context_length' in info:
            return int(info['context_length'])
        elif 'parameters' in info and 'context_length' in info['parameters']:
            return int(info['parameters']['context_length'])
    except Exception:
        pass
    # Fallback to 32768 if not found
    print("Failed to find model's max context length.")
    return 32768

MAX_INPUT_TOKENS = get_model_context_length(OLLAMA_MODEL)
TOKEN_WARN_THRESHOLD = int(MAX_INPUT_TOKENS * 0.8)









def load_jsonl(file_path: str) -> List[Dict]:
    """Load a JSONL file into a list of dicts."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def load_txt(file_path: str) -> str:
    """Load a plain text file as context."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def build_context(paragraphs: List[Dict]) -> str:
    """Format paragraphs for context to send to LLM."""
    context = []
    for p in paragraphs:
        header = p.get('header', '')
        page = p.get('page', None)
        para = p.get('paragraph', '')
        context.append(f"[Header: {header}] [Page: {page}]\n{para}")
    return '\n\n'.join(context)


def count_tokens(text: str) -> int:
    # Simple token estimate: 1 token ≈ 4 chars (for English, rough)
    return len(text) // 4

def ask_ollama(context: str, question: str, memory: list, model: str = 'llama3') -> str:
    """Send context, memory, and question to Ollama and get a response."""
    # Compose messages: memory (as chat), then RAG context, then user question
    messages = []
    for m in memory:
        messages.append(m)
    # Add system prompt with directive, conversation log, and repeated user question
    # Build conversation log string
    conversation_log = "\n".join([
        f"[USER] {m['content']}" if m['role'] == 'user' else f"[NHP] {m['content']}"
        for m in memory
    ])
    directive = (
        "You are an NHP within the LANCER universe tasked with answering user questions. Utilize the context available to you to answer the user's question to the best of your ability. "
        "You will be provided a portion of the LANCER core rule book for which to base your answers on."
        f"{NHP_PROMPT if NHP_PROMPT else ''}"
        "If you can't answer the question, instead provide a reason as to why. "
        "If the context is long, prioritize the user's question above all else.\n"
        "When answering the question, it is very important that you only answer using data from the context. Do not make up new context. If the question can't be answered with the provided context, explain so to the user.\n"
        "---\n"
        "IMPORTANT: The following is the reference CONTEXT. It is NOT the user's question. Do not treat the context as a question. Only use it as supporting information.\n"
        "After the context, you will see the a conversation log and the USER'S QUESTION. Only answer the user's question, using the context as reference.\n"
        "---\n"
        f"CONTEXT STARTS:\n{context}\nCONTEXT ENDS\n"
        "---\n"
        "CONVERSATION LOG (this is the chat history so far, use it to maintain continuity):\n"
        f"{conversation_log}\n"
        f"USER QUESTION: {question}\n"
        "---\n"
        "Again: Do NOT treat the context as a question. Only answer the user's question, using the context as reference."
        "Please give your response to the user's question:"
    )
    # === Suggestions for higher-impact/complexity improvements ===
    #
    # 1. Implement context chunking/sliding window: If the combined context exceeds the model's token limit, automatically select the most relevant chunks based on the user's question (using keyword matching, embeddings, or a vector database).
    # 2. Add support for PDF or DOCX context ingestion directly, with automatic conversion to text or JSONL.
    # 3. Integrate semantic search or retrieval-augmented generation (RAG) with vector stores (e.g., FAISS, ChromaDB) for more scalable and relevant context retrieval.
    # 4. Add a web-based or more advanced GUI (e.g., using PyQt, Electron, or a web frontend) for a richer user experience.
    # 5. Implement user authentication and multi-user conversation memory.
    # 6. Add context source attribution in answers (cite which file/section the answer is based on).
    # 7. Support for streaming responses from Ollama for a more interactive chat experience.
    # 8. Add logging, analytics, and error reporting for monitoring usage and debugging.
    # 9. Allow context files to be specified via command-line arguments or a config file for more flexible deployment.
    # 10. Add automated tests and CI/CD integration for robust development.
    messages.append({"role": "system", "content": directive})
    messages.append({"role": "user", "content": question})
    total_input = '\n'.join([m['content'] for m in messages])
    input_tokens = count_tokens(total_input)
    token_msg = f"[Token usage: {input_tokens} / {MAX_INPUT_TOKENS} tokens]"
    if input_tokens >= MAX_INPUT_TOKENS:
        token_msg += "\n[WARNING: Input exceeds model max tokens! Response may be truncated or fail.]"
    elif input_tokens >= TOKEN_WARN_THRESHOLD:
        token_msg += f"\n[Warning: Approaching model max tokens ({TOKEN_WARN_THRESHOLD})]"
    messages.append({"role": "system", "content": token_msg})
    response = ollama.chat(model=model, messages=messages)
    return response['message']['content'], token_msg # type: ignore



# --- Memory functions for GUI ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_memory(memory):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':

    def get_context_from_files(context_files):
        contexts = []
        for context_file in context_files:
            if not os.path.exists(context_file):
                print(f"File not found: {context_file}")
                exit(1)
            if context_file.lower().endswith('.jsonl'):
                data = load_jsonl(context_file)
                contexts.append(build_context(data))
            elif context_file.lower().endswith('.txt'):
                contexts.append(load_txt(context_file))
            else:
                print(f"Unsupported file type: {context_file}. Please provide a .jsonl or .txt file.")
                exit(1)
        return '\n\n---\n\n'.join(contexts)

    if DEBUG_CONTEXT_MODE:
        rag_context = get_context_from_files(CONTEXT_FILES)
        memory = load_memory()
        user_input = input("Enter a sample user prompt to debug context: ")
        # Compose messages as in ask_ollama
        messages = []
        for m in memory:
            messages.append(m)
        messages.append({"role": "system", "content": f"Reference context for this session:\n{rag_context}"})
        messages.append({"role": "user", "content": user_input})
        total_input = '\n'.join([m['content'] for m in messages])
        input_tokens = count_tokens(total_input)
        token_msg = f"[Token usage: {input_tokens} / {MAX_INPUT_TOKENS} tokens]"
        if input_tokens >= MAX_INPUT_TOKENS:
            token_msg += "\n[WARNING: Input exceeds model max tokens! Response may be truncated or fail.]"
        elif input_tokens >= TOKEN_WARN_THRESHOLD:
            token_msg += "\n[Warning: Approaching model max tokens.]"
        # Write all context to dummy file
        with open("dummy_context_debug.txt", "w", encoding="utf-8") as f:
            f.write("--- DEBUG CONTEXT MODE ---\n\n")
            for i, m in enumerate(messages):
                f.write(f"[{m['role'].upper()}] {str(m['content'])}\n\n")
            f.write(token_msg + "\n")
    else:
        rag_context = get_context_from_files(CONTEXT_FILES)
        # Pass all required functions and variables to start_gui, including rag_context
        start_gui(
            JSONL_FILE=CONTEXT_FILES,
            CONTEXT_FILE=MEMORY_FILE,
            OLLAMA_MODEL=OLLAMA_MODEL,
            TOKEN_WARN_THRESHOLD=TOKEN_WARN_THRESHOLD,
            MAX_INPUT_TOKENS=MAX_INPUT_TOKENS,
            load_jsonl=load_jsonl,
            build_context=build_context,
            load_memory=load_memory,
            save_memory=save_memory,
            ask_ollama=ask_ollama,
            count_tokens=count_tokens,
            rag_context=rag_context
        )
