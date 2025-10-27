import re
import requests
from typing import Dict
from collections import Counter

class TextPreprocessor:
    def _strip_gutenberg_headers(self, text: str) -> str:
        start = re.search(r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK.*\*\*\*", text, re.IGNORECASE)
        end = re.search(r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK.*\*\*\*", text, re.IGNORECASE)
        if start:
            text = text[start.end():]
        if end:
            text = text[:end.start()]
        return text.strip()

    def _clean_text_basic(self, text: str) -> str:
        text = text.replace('\r', '\n').replace('\x00', '')
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)
        return text.strip()

    def fetch_from_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")) or ".txt" not in url:
            raise ValueError("Please provide a valid .txt URL (e.g., a Project Gutenberg link).")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        r.encoding = r.encoding or "utf-8"
        return r.text

    def get_text_statistics(self, text: str) -> Dict:
        if not text.strip():
            return {
                "total_characters": 0,
                "total_words": 0,
                "total_sentences": 0,
                "avg_word_length": 0.0,
                "avg_sentence_length": 0.0,
                "most_common_words": []
            }
        words = re.findall(r"[A-Za-z']+", text)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        total_words = len(words)
        total_sentences = len([s for s in sentences if s.strip()])
        avg_word = sum(len(w) for w in words) / total_words if total_words else 0
        avg_sent = total_words / total_sentences if total_sentences else 0
        freq = Counter(w.lower() for w in words).most_common(10)
        return {
            "total_characters": len(text),
            "total_words": total_words,
            "total_sentences": total_sentences,
            "avg_word_length": round(avg_word, 3),
            "avg_sentence_length": round(avg_sent, 3),
            "most_common_words": [{"word": w, "count": c} for w, c in freq]
        }

    def create_summary(self, text: str, num_sentences: int = 3) -> str:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if len(s.strip()) > 10]
        return " ".join(sentences[:num_sentences])

    def full_clean(self, raw_text: str) -> str:
        return self._clean_text_basic(self._strip_gutenberg_headers(raw_text))
