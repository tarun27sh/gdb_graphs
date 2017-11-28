# Python_gdb_networkx_graphs

![Alt text](yup.png?raw=true "")


## Description  
Python command line tool to visualize function-call-flow for a C program using di-graphs from networkx library (and matplotlib).

## Motivation  
I wanted to view call-graph for OS source (written in C) that connected APIs within one layer and APIs across layers.
This helps in getting a bigger picture of the source code and makes understanding large code bases QUICK.

## Input  
Requires data from gdb to get nodes (functions) and edges (function 1 calling function 2).

## Output  
Di-graph showing relationship between functions across software layers, the "bigger picture".
