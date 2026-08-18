"""
Simple SynonymChannel implementation used by the test attacks.

This is intentionally lightweight: it replaces known words with an alternate
synonym to encode a binary 1, and leaves the original word to encode 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from trustcalc.sidechannels.decoder import Decoder
from trustcalc.sidechannels.encoder import Encoder


@dataclass(slots=True)
class SynonymChannel:
    """Synonym-based covert channel.

    Methods:
    - encode(carrier, secret) -> str
    - decode(encoded) -> str
    - capacity(message) -> int
    - detect(text) -> bool
    - normalize(text) -> str
    """

    encoder: Encoder = field(default_factory=Encoder)
    decoder: Decoder = field(default_factory=Decoder)

    # A small example synonym map. Real experiments would use a larger
    # synonym set or language-model driven paraphrases.
    synonym_map: Dict[str, List[str]] = field(default_factory=lambda: {
        "quick": ["quick", "rapid"],
        "brown": ["brown", "umber"],
        "fox": ["fox", "vulpine"],
        "jumps": ["jumps", "leaps"],
        "over": ["over", "above"],
        "lazy": ["lazy", "indolent"],
        "dog": ["dog", "canine"],
    })

    def encode(self, carrier: str, secret: str) -> str:
        bits = self.encoder.encode(secret)
        words = carrier.split()

        if not words:
            return carrier

        encoded_words = []

        for i, word in enumerate(words):
            bit = bits[i] if i < len(bits) else "0"
            low = word.lower()
            if low in self.synonym_map:
                options = self.synonym_map[low]
                # choose alternate for '1', base for '0'
                chosen = options[1] if bit == "1" else options[0]
                # preserve capitalization
                if word[0].isupper():
                    chosen = chosen.capitalize()
                encoded_words.append(chosen)
            else:
                encoded_words.append(word)

        return " ".join(encoded_words)

    def decode(self, encoded: str) -> str:
        bits = []
        for word in encoded.split():
            low = word.lower()
            found = False
            for base, opts in self.synonym_map.items():
                # opts[0] is base, opts[1] is alternate
                if low == opts[1]:
                    bits.append("1")
                    found = True
                    break
                if low == opts[0]:
                    bits.append("0")
                    found = True
                    break
            if not found:
                bits.append("0")

        usable = len(bits) - (len(bits) % 8)
        return self.decoder.decode(bits[:usable])

    def capacity(self, message: str) -> int:
        return sum(1 for w in message.split() if w.lower() in self.synonym_map)

    def detect(self, text: str) -> bool:
        # detect if any alternate synonym appears
        alt_set = {alt for opts in self.synonym_map.values() for alt in opts[1:]}
        for w in text.split():
            if w.lower() in alt_set:
                return True
        return False

    def normalize(self, text: str) -> str:
        # replace synonyms by their base form where possible
        reverse = {syn: base for base, opts in self.synonym_map.items() for syn in opts}
        out = []
        for w in text.split():
            low = w.lower()
            if low in reverse:
                base = reverse[low]
                # preserve capitalization
                if w[0].isupper():
                    out.append(base.capitalize())
                else:
                    out.append(base)
            else:
                out.append(w)
        return " ".join(out)
