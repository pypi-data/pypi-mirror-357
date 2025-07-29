# AutoLyap

A Python package for automated Lyapunov-based convergence analysis of first-order optimization and inclusion methods.

---

## Overview

AutoLyap streamlines the process of constructing and verifying Lyapunov analyses by formulating them as semidefinite programs (SDPs). It supports a broad class of structured optimization and inclusion problems, automating proofs of linear or sublinear convergence rates for many well‑known algorithms.

## Documentation

Full user guide and API reference:
➡️  [https://autolyap.github.io](https://autolyap.github.io/)

## Installation

```bash
pip install autolyap
```

AutoLyap depends on:

* [NumPy](https://numpy.org/) 
* [MOSEK](https://www.mosek.com/) (academic license available)