

import os
import tkinter as tk
from tkinter import messagebox
import threading

# MarkdownText fallback: always use tk.Text (MarkdownText not available)
MarkdownText = tk.Text


def start_gui(
	JSONL_FILE,
	CONTEXT_FILE,
	OLLAMA_MODEL,
	TOKEN_WARN_THRESHOLD,
	MAX_INPUT_TOKENS,
	load_jsonl,
	build_context,
	load_memory,
	save_memory,
	ask_ollama,
	count_tokens,
	rag_context
):
	memory = load_memory()

	def get_current_context_tokens():
		# Combine context and memory
		messages = []
		for m in memory:
			messages.append(m)
		messages.append({"role": "system", "content": f"Reference context for this session:\n{rag_context}"})
		total_input = '\n'.join([m['content'] for m in messages])
		return count_tokens(total_input)

	root = tk.Tk()
	root.title("NHP RAG Chat (Ollama)")

	chat_display = MarkdownText(root, width=100, height=30, wrap=tk.WORD)
	chat_display.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
	chat_display.config(state='disabled')

	entry = tk.Entry(root, width=80)
	entry.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

	context_tokens = get_current_context_tokens()
	if context_tokens >= TOKEN_WARN_THRESHOLD:
		token_label = tk.Label(root, text=f"Warning! Token count approaching max: {context_tokens} / {MAX_INPUT_TOKENS}")
	else:
		token_label = tk.Label(root, text=f"Current token count: {context_tokens} / {MAX_INPUT_TOKENS}")
	token_label.grid(row=2, column=0, sticky='w', padx=5)

	def render_conversation():
		chat_display.config(state='normal')
		chat_display.delete('1.0', tk.END)
		# Render all messages in memory as markdown
		for m in memory:
			if m['role'] == 'user':
				chat_display.insert(tk.END, f"**You:** {m['content']}\n\n")
			elif m['role'] == 'assistant':
				chat_display.insert(tk.END, f"**NHP:** {m['content']}\n\n")
		chat_display.config(state='disabled')
		chat_display.see(tk.END)

	def send():
		user_input = entry.get().strip()
		if not user_input:
			return
		entry.config(state='disabled')
		send_btn.config(state='disabled')
		chat_display.config(state='normal')
		chat_display.insert(tk.END, f"**You:** {user_input}\n\n")
		chat_display.insert(tk.END, "**NHP:** [Thinking...]\n\n")
		chat_display.config(state='disabled')
		chat_display.see(tk.END)
		def worker():
			try:
				answer, token_msg = ask_ollama(rag_context, user_input, memory, model=OLLAMA_MODEL)
			except Exception as e:
				answer = f"[Error: {e}]"
				token_msg = ""
			memory.append({"role": "user", "content": user_input})
			memory.append({"role": "assistant", "content": answer})
			save_memory(memory)
			def update_display():
				render_conversation()
				chat_display.config(state='normal')
				chat_display.insert(tk.END, f"*{token_msg}*\n\n")
				chat_display.config(state='disabled')
				chat_display.see(tk.END)
				entry.config(state='normal')
				send_btn.config(state='normal')
				# Update context token label
				context_tokens = get_current_context_tokens()
				token_label.config(text=f"Model max tokens: {MAX_INPUT_TOKENS} | Warning at: {TOKEN_WARN_THRESHOLD} | Current context: {context_tokens}")
			root.after(0, update_display)
		threading.Thread(target=worker, daemon=True).start()

	entry.bind('<Return>', lambda event: send())
	send_btn = tk.Button(root, text="Send", command=send)
	send_btn.grid(row=1, column=1, padx=5, pady=5)

	render_conversation()

	root.mainloop()
