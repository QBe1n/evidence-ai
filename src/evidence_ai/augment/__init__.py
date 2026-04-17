"""Synthetic trial data augmentation module.

Implements the TrialSynth model for generating synthetic sequential clinical
trial data while preserving temporal event patterns.

Architecture:
  Input (event_types, timestamps)
    → Transformer Encoder (sinusoidal temporal + causal self-attention)
    → Latent space z ~ N(μ, σ² × var_multiplier)
    → Linear decoder → Hawkes process decoder
    → Synthetic event sequences

Based on:
  https://github.com/chufangao/TrialSynth
  (Georgia Tech, NeurIPS 2024 Workshop, MIT License)
"""

from evidence_ai.augment.synth import TrialSynthAugmentor

__all__ = ["TrialSynthAugmentor"]
