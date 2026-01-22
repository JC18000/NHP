# NHP
A custom RAG-based solution for extracting complex PDFs and cleaning the results, combined with an AI chatbot taking inspiration from the LANCER universe.

The system is intended to be able to answer user questions strictly using the provided context, as well as supporting a writing style that fits the universe.

While nominally tied to the LANCER ttrpg (table-top roleplaying game) system, by changing the system prompt and feeding in different context, this can easily be extrapolated to create context-rich agents.

## The framework

1. A raw PDF is fed in
2. The PDF has it's text extracted using pymupdf4llm (I've tried others, this one provided the best result for me due to the complex structure).
3. The output from pymupdf4llm is then chunked by page and cleaned by an AI system tasked to clean OCR errors.
4. (Optionally) The cleaned output gets chunked by paragraph and turned into a JSONL file
5. That JSONL file (or the cleaned plaintext from step 3) is then fed into a RAG-based AI setup. The system is set up to handle multiple input files at once.
6. Everything runs locally using Ollama, and *isn't* super slow when doing so.

## Current capabilities (assuming I keep this readme up to date)
1. Perform the chopping up, slicing, dicing, and everything-nicing of a perfectly good PDF into an ugly plaintext file
2. Run an chatbot "application" (Tkinter GUI built in 30 seconds) using frankly way too much context to run with the response times it does

Sure, this doesn't sound impressive, but the version number is currently -1.0, which is to say it's nowhere close to demo-able.
I may seem unprofessional here, but that's because this is, strictly speaking, a hobby project. Mind the CamelCase, please (one way to tell what wasn't AI generated, at least...).

## Challenges

1. Extracting the PDF: This one took me a long time experimenting to get a solution that both worked, and worked *well*. I don't want to manually parse the plaintext output of a ~500 page PDF for errors by hand. Also, the PDF that I am using contains custom glyphs embedded in the text. Thankfully, all I needed for that was to translate the unicode value to a plaintext name (i.e "" became "ACCURACY") Even with that, pymupdf can only handle so much, and there are often letter combos that result in unknown unicode values. That's what the cleaner is for.
2. Cleaning the PDF: This was much less of a headache than the other steps. The only struggle was finding out why a ~20 page input PDF was getting chunked into ~500 segments. Once I got that sorted out, the rest was classic prompt engineering. Namely, getting the AI I was using to *only* output the cleaned text, to *only* clean the text, and to not hallucinate 1960s British rock band *The Cavarly* into the PDF (yes, that happened).
3. Token and context issues: This is the only real challenge that remains, not due to code architecture but due to the limits of the system I am using. Namely, the problem is that I am essentially drowning the model in tokens, forcing me to use a 32k token model (currently qwen2.5:7b-instruct-q4_K_M at time of writing), but there is a chance I will have to upgrade to a 64k or even 128k model later down the line, since a simple 20-page chunk is getting me concerningly close to the token limit. Of course, this also means I will probably have to factor in another solution, likely being selective over what context the model gets to use.
4. Token and context issues (again): The other problem with drowning an LLM in tokens is that *I'm drowning an LLM in tokens*. They don't like that very much, and make their displeasure known by *completely ignoring the system prompt, user prompt, and conversation log* in favor of treating the massive block of context as if it was the user prompt, or a part of it. This may seem like another prompt engineering problem, but in reality, when 95% of your context window is used as context, the model ends up weighting that much more strongly than the rest, just because there's just so *much* of it. Realistically, I will have to use selective context sooner rather than later.
5. Future me problems: Other than the issues I described above, I will, sooner or later, have to deal with finding a way to get around LANCER's very much nonstandard table design. I already have an automatic extractor for NPC statblocks that I'm proud of, but that took time and can't be extrapolated to other tables in the book. A solution that can automatically grab content from all tables automatically, likely using another built-in LLM, will have to be built. The upside to this is that it also extrapolates to *any* table in *any* PDF, once again making this system usable for anything but LANCER.

## Aspirations
Or; what I would like to implement in the future if I could, regardless of if I'm able to.
1. Full capability to roleplay as a player in a functioning LANCER game. This could simply be a system for roleplaying, with real humans at the table controlling the pilot in combat, but it would be cool if it could be interfaced with LANCER's notably crunchy combat system (if you don't know that the term "crunchy" means in this context, don't worry about it).
2. Full capacity to adapt to any PDF, and not just for tabletop games. I want this thing to have at least *some* business value, y'know.
3. If I can fulfill that first aspiration, the logical conclusion is to make an AI system capable of *running* a LANCER campaign. And if I can fulfill the second, then that becomes an AI system capable of running *any* table-top RPG. Howver, this one is a lot more far-fetched, and knowing the tabletop community, would probably be rejected.

However, the first goal is to make it function as an assistant first, and potentially roleplay as a player's NHP system in-game second.

## Legal, notes, and witty remarks

*This program is not an official* Lancer *product; it is a third party work, and is not affiliated with Massif Press. This program is published via the* Lancer *Third Party License.*
Lancer *is copyright Massif Press*

***Also: I will NOT be posting the paid version of the LANCER core book in this repo, even though I'm using it locally on my machine. If you wanted to pirate it, don't. LANCER is something great, and it's creators deserve your money.***

If you want to use this sytem with the full core book (or any PDF), I will likely be implementing a pipeline system that can perform steps 2-6 automatically for any PDF without having to feed it through the system manually. However, if you plan on using this with non-LANCER content, I would highly recommend changing the system prompt.

*For pedants who just so happen to be familiar with the LANCER universe:*
Yes, I know. What I built here is, by definition, a *Comp/Con* and not an *NHP*. However, Comp/Con is already the name of a great tool for LANCER, and there's this perfectly good term for highly-advanced, sentient intelligences right there... hence NHP. Also, I doubt we'll be discovering Deimos Entities any time in the near future.
