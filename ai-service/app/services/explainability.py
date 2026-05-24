# app/services/explainability.py

import re
import time
import logging
import torch
import numpy as np
import torch.nn as nn
import pytorch_lightning as pl

from typing import Dict
from transformers import (
    AutoTokenizer,
    AutoModel
)

from captum.attr import (
    LayerIntegratedGradients
)

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# ============================================================
# DEVICE
# ============================================================

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

logger.info(f"Using device: {DEVICE}")

# ============================================================
# LABELS
# ============================================================

LABELS = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_attack"
]

# ============================================================
# STOPWORDS
# ============================================================

STOPWORDS = {
    "the", "a", "an", "you", "i",
    "he", "she", "it", "this",
    "that", "is", "are", "was",
    "were", "to", "of", "and",
    "in", "on", "for", "your",
    "my", "our", "their", "be",
    "been", "am", "do", "does",
    "did", "have", "has", "had"
}

# ============================================================
# LIGHTNING MODEL
# ============================================================


class ToxicClassifier(pl.LightningModule):

    def __init__(
        self,
        model_name="roberta-base",
        num_labels=6,
        lr=None,
        label_smoothing=None
    ):

        super().__init__()

        self.backbone = AutoModel.from_pretrained(
            model_name
        )

        hidden_size = (
            self.backbone.config.hidden_size
        )

        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, num_labels)
        )

    def forward(
        self,
        input_ids,
        attention_mask
    ):

        outputs = self.backbone(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        cls_output = (
            outputs.last_hidden_state[:, 0, :]
        )

        logits = self.classifier(cls_output)

        return logits


# ============================================================
# EXPLAINER
# ============================================================


class ToxicIntegratedExplainer:

    def __init__(
        self,
        checkpoint_path: str,
        model_name: str = "roberta-base",
        max_len: int = 128
    ):

        logger.info(
            "Initializing explainability engine..."
        )

        self.device = DEVICE

        self.max_len = max_len

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                model_name
            )
        )

        logger.info(
            f"Loading trained checkpoint: {checkpoint_path}"
        )

        self.model = (
            ToxicClassifier.load_from_checkpoint(
                checkpoint_path,
                model_name=model_name,
                num_labels=len(LABELS)
            )
        )

        self.model.eval()

        self.model.to(self.device)

        logger.info(
            "Initializing Integrated Gradients..."
        )

        self.lig = LayerIntegratedGradients(
            self.forward_func,
            self.model.backbone.embeddings
        )

        logger.info(
            "Explainability engine ready"
        )

    # ========================================================
    # FORWARD FUNCTION
    # ========================================================

    def forward_func(
        self,
        input_ids,
        attention_mask
    ):

        logits = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        probs = torch.sigmoid(logits)

        return probs

    # ========================================================
    # TOKEN MERGING
    # ========================================================

    def merge_tokens(
        self,
        tokens,
        scores
    ):

        merged_tokens = []

        merged_scores = []

        current_word = ""

        current_scores = []

        for token, score in zip(
            tokens,
            scores
        ):

            if token in [
                "<s>",
                "</s>",
                "<pad>"
            ]:
                continue

            if token.startswith("Ġ"):

                if current_word:

                    merged_tokens.append(
                        current_word
                    )

                    merged_scores.append(
                        np.mean(current_scores)
                    )

                current_word = token.replace(
                    "Ġ",
                    ""
                )

                current_scores = [score]

            else:

                current_word += token

                current_scores.append(score)

        if current_word:

            merged_tokens.append(current_word)

            merged_scores.append(
                np.mean(current_scores)
            )

        return merged_tokens, merged_scores

    # ========================================================
    # BUILD PHRASES
    # ========================================================

    def build_phrases(
        self,
        words,
        scores
    ):

        phrases = []

        for i in range(len(words) - 1):

            phrase = (
                f"{words[i]} {words[i+1]}"
            )

            phrase_score = (
                scores[i] + scores[i+1]
            ) / 2

            phrases.append(
                (phrase, phrase_score)
            )

        phrases = sorted(
            phrases,
            key=lambda x: x[1],
            reverse=True
        )

        return phrases[:5]

    # ========================================================
    # GENERATE REASON
    # ========================================================

    def generate_reason(
        self,
        labels,
        toxic_phrases
    ):

        reasons = []

        if "threat" in labels:

            reasons.append(
                "Contains threatening or intimidating language."
            )

        if "insult" in labels:

            reasons.append(
                "Contains direct personal insults."
            )

        if "obscene" in labels:

            reasons.append(
                "Contains offensive or abusive wording."
            )

        if "identity_attack" in labels:

            reasons.append(
                "Contains identity-targeted harmful language."
            )

        if not reasons:

            reasons.append(
                "General toxic language detected."
            )

        if toxic_phrases:

            joined = ", ".join([
                f'"{p}"'
                for p in toxic_phrases[:3]
            ])

            reasons.append(
                f"Key toxic phrases: {joined}."
            )

        return " ".join(reasons)

    # ========================================================
    # FAST PREDICTION
    # ========================================================

    def predict_only(
        self,
        text: str
    ):

        logger.info(
            "Running fast prediction..."
        )

        encoding = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=self.max_len
        )

        input_ids = (
            encoding["input_ids"]
            .to(self.device)
        )

        attention_mask = (
            encoding["attention_mask"]
            .to(self.device)
        )

        with torch.no_grad():

            logits = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

            probs = (
                torch.sigmoid(logits)
                .squeeze()
                .cpu()
                .numpy()
            )

        toxic_score = float(probs[0])

        triggered_labels = [

            LABELS[i]

            for i, p in enumerate(probs)

            if p > 0.5
        ]

        return {

            "text": text,

            "is_toxic": toxic_score > 0.5,

            "confidence": round(
                toxic_score,
                4
            ),

            "labels": {

                LABELS[i]: round(
                    float(probs[i]),
                    4
                )

                for i in range(len(LABELS))
            },

            "triggered_labels": triggered_labels,

            "input_ids": input_ids,

            "attention_mask": attention_mask
        }

    # ========================================================
    # FULL EXPLAINABILITY
    # ========================================================

    def explain(
        self,
        text: str
    ) -> Dict:

        logger.info(
            "Starting explainability pipeline..."
        )

        total_start = time.time()

        prediction = self.predict_only(text)

        # ====================================================
        # SAFE SHORT-CIRCUIT
        # ====================================================

        if not prediction["is_toxic"]:

            logger.info(
                "Safe content detected. Skipping Captum."
            )

            return {

                "text": text,

                "is_toxic": False,

                "confidence": prediction[
                    "confidence"
                ],

                "labels": prediction[
                    "labels"
                ],

                "triggered_labels": [],

                "top_words": [],

                "toxic_phrases": [],

                "reason": (
                    "Safe content detected."
                )
            }

        logger.info(
            "Toxic content detected. Running Integrated Gradients..."
        )

        input_ids = prediction["input_ids"]

        attention_mask = prediction[
            "attention_mask"
        ]

        # ====================================================
        # ATTRIBUTION
        # ====================================================

        attr_start = time.time()

        attributions, delta = (
            self.lig.attribute(

                inputs=input_ids,

                additional_forward_args=(
                    attention_mask,
                ),

                target=0,

                return_convergence_delta=True
            )
        )

        logger.info(
            f"Integrated gradients completed in "
            f"{time.time() - attr_start:.2f}s"
        )

        attributions = (
            attributions
            .sum(dim=-1)
            .squeeze(0)
        )

        attributions = (
            attributions
            .detach()
            .cpu()
            .numpy()
        )

        attributions = attributions / (
            np.linalg.norm(attributions)
            + 1e-8
        )

        tokens = (
            self.tokenizer.convert_ids_to_tokens(
                input_ids.squeeze(0)
            )
        )

        words, scores = self.merge_tokens(
            tokens,
            attributions
        )

        # ====================================================
        # FILTERING
        # ====================================================

        filtered = []

        for word, score in zip(
            words,
            scores
        ):

            clean_word = re.sub(
                r"[^a-zA-Z]",
                "",
                word
            ).lower()

            if clean_word in STOPWORDS:
                continue

            if len(clean_word) <= 1:
                continue

            filtered.append(
                (word, score)
            )

        filtered = sorted(
            filtered,
            key=lambda x: x[1],
            reverse=True
        )

        # ====================================================
        # PHRASES
        # ====================================================

        logger.info(
            "Generating toxic phrases..."
        )

        top_words = [
            w for w, s in filtered[:10]
        ]

        top_scores = [
            s for w, s in filtered[:10]
        ]

        phrases = self.build_phrases(
            top_words,
            top_scores
        )

        toxic_phrases = [

            p for p, s in phrases

            if s > 0
        ]

        # ====================================================
        # REASON
        # ====================================================

        reason = self.generate_reason(
            prediction["triggered_labels"],
            toxic_phrases
        )

        logger.info(
            f"Total explainability completed in "
            f"{time.time() - total_start:.2f}s"
        )

        return {

            "text": text,

            "is_toxic": True,

            "confidence": prediction[
                "confidence"
            ],

            "labels": prediction[
                "labels"
            ],

            "triggered_labels": prediction[
                "triggered_labels"
            ],

            "top_words": [

                {
                    "word": w,

                    "importance": round(
                        float(s),
                        4
                    )
                }

                for w, s in filtered[:10]
            ],

            "toxic_phrases": toxic_phrases[:5],

            "reason": reason
        }
