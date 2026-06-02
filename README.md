# HDC Branch Predictor

A Python implementation of an online branch predictor using 
hyperdimensional computing (HDC), built during a summer 2024 
research internship at Stanford University with Professor Sara 
Achour (LINXS Lab).

## Background

Branch prediction is a hardware optimization that guesses whether 
a conditional branch (if/else, loop, etc.) will be taken or not 
before the outcome is known, allowing the processor to speculatively 
execute ahead. Mispredictions are expensive.

This project explores whether hyperdimensional computing—a 
mathematical framework that represents data as high-dimensional 
binary vectors and encodes history through algebraic operations on 
those vectors—can serve as an effective basis for branch prediction. 
The central question: can the outcome of a branch be predicted from 
a compact HDC encoding of all past execution decisions?

## Files

- `hdc.py`: core HDC encoding and operations
- `hdc-branch-pred.py`: HDC-based branch predictor
- `two_bit_predictor.py`: baseline two-bit saturating counter 
  predictor for comparison
- `rev_list.py`: utilities for processing branch trace data
- `hdc/`: additional HDC modules

## Usage

```bash
python hdc-branch-pred.py <trace_file>
python two_bit_predictor.py <trace_file>
```

Trace files should be in branch-prediction competition format.

## Dependencies

Python standard library and NumPy.
