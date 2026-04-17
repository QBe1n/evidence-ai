"""Specialized clinical outcome extraction using BiomedBERT (EvidenceOutcomes).

Implements a focused BiomedBERT-base model trained on 640 expert-annotated
abstracts (inter-rater agreement 0.76) for clinical outcome detection using
IOB2 tagging (B-Outcome, I-Outcome, O).

Used as a high-precision refinement layer on top of PICOX outcome spans.

Based on:
  https://github.com/ebmlab/EvidenceOutcomes (Columbia University ebmlab, MIT License)

IOB2 tagging scheme:
  B-Outcome: Beginning token of an outcome span
  I-Outcome: Continuation token of an outcome span
  O: Outside any outcome span
"""

from __future__ import annotations

import logging
from typing import Any

from evidence_ai.extract.models import EntitySpan, SpanLabel

logger = logging.getLogger(__name__)

# IOB2 labels for outcome tagging
IOB2_LABELS = ["O", "B-Outcome", "I-Outcome"]
LABEL2ID = {label: i for i, label in enumerate(IOB2_LABELS)}
ID2LABEL = {i: label for i, label in enumerate(IOB2_LABELS)}

DEFAULT_OUTCOME_CONFIDENCE = 0.65


class OutcomeExtractor:
    """Extract clinical outcome spans using BiomedBERT-base with IOB2 tagging.

    This model provides higher precision for outcome detection compared to
    the general PICOX model, at the cost of narrower coverage (outcomes only).

    Args:
        model_path: HuggingFace model ID or local path for the fine-tuned model.
        device: Compute device (``"cpu"``, ``"cuda"``, or ``"mps"``).
        confidence_threshold: Minimum confidence for span inclusion.
    """

    def __init__(
        self,
        model_path: str,
        device: str = "cpu",
        confidence_threshold: float = DEFAULT_OUTCOME_CONFIDENCE,
    ) -> None:
        self.model_path = model_path
        self.device = device
        self._threshold = confidence_threshold
        self._model: Any = None
        self._tokenizer: Any = None

    @classmethod
    def from_pretrained(
        cls,
        model_path: str = "sultan/BiomedNLP-BiomedBERT-base-uncased-abstract",
        device: str = "cpu",
        confidence_threshold: float = DEFAULT_OUTCOME_CONFIDENCE,
    ) -> "OutcomeExtractor":
        """Instantiate an OutcomeExtractor with the specified model.

        After fine-tuning on the EvidenceOutcomes dataset, replace
        ``model_path`` with the local path to the fine-tuned weights.

        Args:
            model_path: HuggingFace model ID or local path (base model or
                fine-tuned checkpoint).
            device: Compute device.
            confidence_threshold: Minimum model confidence to include a span.

        Returns:
            Configured :class:`OutcomeExtractor` instance.
        """
        return cls(
            model_path=model_path,
            device=device,
            confidence_threshold=confidence_threshold,
        )

    def _load_model(self) -> None:
        """Lazy-load the BiomedBERT token classification model."""
        # TODO: Load fine-tuned BiomedBERT model for outcome extraction
        # Steps:
        # 1. Download EvidenceOutcomes dataset from ebmlab
        # 2. Fine-tune BiomedBERT-base on IOB2 outcome annotations
        # 3. Save fine-tuned model and set model_path to saved checkpoint
        #
        # from transformers import AutoTokenizer, AutoModelForTokenClassification
        # import torch
        #
        # self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        # self._model = AutoModelForTokenClassification.from_pretrained(
        #     self.model_path,
        #     num_labels=len(IOB2_LABELS),
        #     id2label=ID2LABEL,
        #     label2id=LABEL2ID,
        # )
        # self._model.to(self.device)
        # self._model.eval()
        logger.warning(
            "OutcomeExtractor using stub implementation. "
            "Fine-tune on EvidenceOutcomes dataset for production use."
        )

    def extract(self, text: str) -> list[EntitySpan]:
        """Extract outcome spans from a single abstract text.

        Args:
            text: The abstract text to process.

        Returns:
            List of :class:`~evidence_ai.extract.models.EntitySpan` objects
            representing identified clinical outcome spans.
        """
        if self._model is None:
            self._load_model()

        # TODO: Implement model inference
        # Steps:
        # 1. Tokenize text with subword offsets
        # 2. Run through token classification model
        # 3. Apply softmax to get probabilities
        # 4. Convert IOB2 predictions to character-offset spans
        # 5. Filter by confidence threshold
        # 6. Map tokens back to original character offsets

        return []

    def extract_batch(self, texts: list[str]) -> list[list[EntitySpan]]:
        """Extract outcome spans from a batch of abstracts.

        Args:
            texts: List of abstract texts.

        Returns:
            List of span lists, one per input text.
        """
        # TODO: implement batched inference for efficiency
        return [self.extract(text) for text in texts]

    @staticmethod
    def _iob2_to_spans(
        tokens: list[str],
        labels: list[str],
        confidences: list[float],
        offsets: list[tuple[int, int]],
    ) -> list[EntitySpan]:
        """Convert IOB2 token predictions to character-offset EntitySpan objects.

        Args:
            tokens: List of tokenized text tokens.
            labels: IOB2 label for each token (``"O"``, ``"B-Outcome"``, ``"I-Outcome"``).
            confidences: Confidence score for each prediction.
            offsets: Character offset (start, end) for each token.

        Returns:
            List of :class:`~evidence_ai.extract.models.EntitySpan` objects.
        """
        spans: list[EntitySpan] = []
        current_start: int | None = None
        current_tokens: list[str] = []
        current_confidences: list[float] = []
        current_end = 0

        for token, label, conf, (start, end) in zip(tokens, labels, confidences, offsets):
            if label == "B-Outcome":
                # Save any in-progress span
                if current_start is not None:
                    avg_conf = sum(current_confidences) / len(current_confidences)
                    spans.append(
                        EntitySpan(
                            text=" ".join(current_tokens),
                            start=current_start,
                            end=current_end,
                            label=SpanLabel.OUTCOME,
                            confidence=avg_conf,
                        )
                    )
                # Start new span
                current_start = start
                current_tokens = [token]
                current_confidences = [conf]
                current_end = end

            elif label == "I-Outcome" and current_start is not None:
                current_tokens.append(token)
                current_confidences.append(conf)
                current_end = end

            else:  # "O"
                if current_start is not None:
                    avg_conf = sum(current_confidences) / len(current_confidences)
                    spans.append(
                        EntitySpan(
                            text=" ".join(current_tokens),
                            start=current_start,
                            end=current_end,
                            label=SpanLabel.OUTCOME,
                            confidence=avg_conf,
                        )
                    )
                    current_start = None
                    current_tokens = []
                    current_confidences = []

        # Finalize any open span
        if current_start is not None:
            avg_conf = sum(current_confidences) / len(current_confidences)
            spans.append(
                EntitySpan(
                    text=" ".join(current_tokens),
                    start=current_start,
                    end=current_end,
                    label=SpanLabel.OUTCOME,
                    confidence=avg_conf,
                )
            )

        return spans
