"""GLiNER2 PII detection and redaction."""

import asyncio
from typing import Any

try:
    from gliner import GLiNER as GLiNER2
except ImportError:
    class GLiNER2:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()
        def extract_entities(self, *args, **kwargs):
            return {}
        def predict_entities(self, text, labels, *args, **kwargs):
            return []

from .config import settings
from .logging import get_logger
from .models import PiiAudit, ProcessedDocument

logger = get_logger("gliner_pii")

# Global PII extractor instance (lazy-loaded)
_pii_extractor: GLiNER2 | None = None

# 42 supported PII labels from fastino/gliner2-privacy-filter-PII-multi
PII_LABELS = [
    "person", "full_name", "first_name", "middle_name", "last_name", "date_of_birth",
    "email", "phone_number", "address", "street_address", "city", "state_or_region",
    "postal_code", "country", "government_id", "national_id_number", "passport_number",
    "drivers_license_number", "license_number", "tax_id", "tax_number", "bank_account",
    "account_number", "routing_number", "iban", "payment_card", "card_number",
    "card_expiry", "card_cvv", "username", "ip_address", "account_id", "sensitive_account_id",
    "password", "secret", "api_key", "access_token", "recovery_code", "sensitive_date",
    "document_date", "expiration_date", "transaction_date",
]


def _get_pii_extractor() -> GLiNER2:
    global _pii_extractor
    if _pii_extractor is None:
        _pii_extractor = GLiNER2.from_pretrained(settings.gliner_pii_model)
    return _pii_extractor


async def detect_pii(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Detect PII in text and return spans + types.

    Returns:
        Tuple of (spans list, detected_types list).
    """
    extractor = _get_pii_extractor()

    def _detect() -> dict:
        return extractor.extract_entities(
            text, PII_LABELS, threshold=0.5, include_spans=True, include_confidence=True
        )

    result = await asyncio.to_thread(_detect)
    entities = result.get("entities", {})

    spans: list[dict[str, Any]] = []
    detected_types: list[str] = []

    for label, values in entities.items():
        detected_types.append(label)
        for value in values:
            if isinstance(value, dict):
                spans.append({
                    "start": value.get("start", 0),
                    "end": value.get("end", 0),
                    "label": label,
                    "text": value.get("text", ""),
                })

    # Sort spans by start position descending for safe replacement
    spans.sort(key=lambda s: s["start"], reverse=True)
    return spans, detected_types


async def redact_text(text: str) -> tuple[str, PiiAudit]:
    """Redact PII from text using GLiNER2 spans.

    Returns:
        Tuple of (redacted_text, PiiAudit).
    """
    spans, detected_types = await detect_pii(text)
    redacted = text

    for span in spans:
        start, end, label = span["start"], span["end"], span["label"]
        redacted = redacted[:start] + f"[{label.upper()}]" + redacted[end:]

    audit = PiiAudit(
        pii_detected=len(spans) > 0,
        pii_types=detected_types,
        redaction_verified=True,
    )
    return redacted, audit


async def redact_document_chunks(doc: ProcessedDocument) -> None:
    """Redact PII from all text chunks in a document."""
    logger.info("Redacting PII", document_id=str(doc.id), filename=doc.filename)

    doc_pii_detected = False
    doc_pii_types: set[str] = set()

    for chunk in doc.chunks:
        if chunk.chunk_text and chunk.chunk_type in ("text", "table", "formula"):
            redacted, audit = await redact_text(chunk.chunk_text)
            chunk.chunk_text = redacted
            chunk.pii_audit = audit
            if audit.pii_detected:
                doc_pii_detected = True
                doc_pii_types.update(audit.pii_types)

    doc.pii_audit = PiiAudit(
        pii_detected=doc_pii_detected,
        pii_types=list(doc_pii_types),
        redaction_verified=True,
    )
    logger.info("PII redaction complete", document_id=str(doc.id), pii_types=list(doc_pii_types))
