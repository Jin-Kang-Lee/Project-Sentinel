import re
import uuid
from typing import Dict, List, Tuple


class PrivacyProxy:
    """Redacts common PII patterns and can restore them later."""

    EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
    PHONE_RE = re.compile(
        r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s.-]?\d{3,4}[\s.-]?\d{4}\b"
    )
    CREDIT_CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
    SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    NRIC_RE = re.compile(r"\b[STFG]\d{7}[A-Z]\b", re.IGNORECASE)

    def __init__(self) -> None:
        self._mapping: Dict[str, str] = {}
        self._counters: Dict[str, int] = {
            "EMAIL": 0,
            "PHONE": 0,
            "CREDIT_CARD": 0,
            "SSN": 0,
            "NRIC": 0,
        }
        self._session_id = uuid.uuid4().hex

    @property
    def mapping(self) -> Dict[str, str]:
        return dict(self._mapping)

    def reset(self) -> None:
        self._mapping.clear()
        for key in self._counters:
            self._counters[key] = 0
        self._session_id = uuid.uuid4().hex

    def redact(self, text: str) -> str:
        if not text:
            return text

        spans = self._collect_spans(text)
        if not spans:
            return text

        redacted = []
        cursor = 0
        for start, end, label, value in spans:
            if start < cursor:
                continue
            redacted.append(text[cursor:start])
            placeholder = self._make_placeholder(label)
            self._mapping[placeholder] = value
            redacted.append(placeholder)
            cursor = end

        redacted.append(text[cursor:])
        return "".join(redacted)

    def deanonymize(self, text: str) -> str:
        if not text or not self._mapping:
            return text

        restored = text
        for placeholder, value in self._mapping.items():
            restored = restored.replace(placeholder, value)
        return restored

    def _make_placeholder(self, label: str) -> str:
        self._counters[label] += 1
        return f"<{label}_{self._counters[label]}>"

    def _collect_spans(self, text: str) -> List[Tuple[int, int, str, str]]:
        spans: List[Tuple[int, int, str, str]] = []

        for match in self.EMAIL_RE.finditer(text):
            spans.append((match.start(), match.end(), "EMAIL", match.group(0)))

        for match in self.PHONE_RE.finditer(text):
            spans.append((match.start(), match.end(), "PHONE", match.group(0)))

        for match in self.SSN_RE.finditer(text):
            spans.append((match.start(), match.end(), "SSN", match.group(0)))

        for match in self.NRIC_RE.finditer(text):
            spans.append((match.start(), match.end(), "NRIC", match.group(0)))

        for match in self.CREDIT_CARD_RE.finditer(text):
            if self._looks_like_credit_card(match.group(0)):
                spans.append((match.start(), match.end(), "CREDIT_CARD", match.group(0)))

        spans.sort(key=lambda item: (item[0], -item[1]))
        return spans

    @staticmethod
    def _looks_like_credit_card(value: str) -> bool:
        digits = re.sub(r"\D", "", value)
        if len(digits) < 13 or len(digits) > 19:
            return False

        checksum = 0
        parity = len(digits) % 2
        for index, digit in enumerate(digits):
            n = int(digit)
            if index % 2 == parity:
                n *= 2
                if n > 9:
                    n -= 9
            checksum += n
        return checksum % 10 == 0
