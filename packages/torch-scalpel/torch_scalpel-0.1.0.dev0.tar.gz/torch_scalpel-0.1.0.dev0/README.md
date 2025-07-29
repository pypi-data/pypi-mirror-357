# torch-scalpel 🔬

> Surgical modifications to PyTorch transformer architectures via FX graph manipulation

## Vision

Traditional research codebases struggle with abstraction design. Predicting where innovation will emerge is impossible, making future-proof APIs elusive. Instead of building rigid abstractions around transformer components, torch-scalpel aims to treat the FX intermediate representation from `torch.compile` as the primary interface for architectural modifications.

We aim to enable surgical precision in transformer research by operating directly on computation graphs as middleware in the torch.compile pipeline. The goal is to swap normalization strategies, evolve attention mechanisms (custom implementations → optimized SDPA), experiment with activation functions... all through targeted graph-level transformations that preserve semantic structure while enabling systematic architectural evolution.

## Status
🚧 **Early Development** - Experimental, viability study phase

## Notebooks
Research notebooks exploring core concepts and validating technical feasibility before designing the library API:
- `compiled_fx_manipulations.ipynb` - FX graph exploration, pattern matching, and surgical transformations
- `replace_attention_in_fx.ipynb` - Transformer attention mechanism replacement (custom → optimized SDPA)