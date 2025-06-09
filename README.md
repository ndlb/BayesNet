# Project 3: Uncertainty

**Group members:**  
Ngoc Dao — `ndao2@u.rochester.edu`  
Luka Avni — `lavni@u.rochester.edu`

## Overview

This Python program performs inference on Bayesian Networks using:
- **Exact inference** via enumeration (`xquery`)
- **Approximate inference** via:
  - Rejection Sampling (`rquery`)
  - Gibbs Sampling (`gquery`)

## How to Run
- To start the program:
    python3 main.py
- To read the Bayesian Network
    load [name of the network file].bn
- To run queries:
    - Exact Inference:
        xquery [query variable] | evidence1=X1 evidence2=X2 evidence3=X3 ...  
    - Approximate with Rejection Sampling:
        rquery [query variable] | evidence1=X1 evidence2=X2 evidence3=X3 ... 
    - Approximate with Gibbs Sampling:
        gquery [query variable] | evidence1=X1 evidence2=X2 evidence3=X3 ... 

