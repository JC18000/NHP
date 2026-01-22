import fitz
import requests
import numpy as np
import faiss
import pymupdf.layout
import pymupdf4llm
from sentence_transformers import SentenceTransformer
import pathlib

GlyphMap = {
    # Damage Types
    "": "Kinetic",
    "": "Explosive",
    "": "Energy",
    "": "Burn",
    "": "Heat",
    # Ranges
    "": "Range",
    "": "Threat",
    # Area Shapes
    "": "Blast",
    "": "Burst",
    "": "Line",
    "": "Cone",
    # Accuracy/Difficulty
    "": "Accuracy",
    "": "Difficulty"
}


plain_text = pymupdf4llm.to_text("CoreBookSnippet 379-382 (NHPs).pdf")

for glyph, replacement in GlyphMap.items():
    plain_text = plain_text.replace(glyph, replacement) # type: ignore

pathlib.Path("Output NHP.txt").write_bytes(plain_text.encode()) # type: ignore

