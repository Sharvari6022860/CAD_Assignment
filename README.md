# VHDL Netlist Levelizer

A Python script to compute **topological gate-level depths** for VHDL netlists.

## Prerequisites

- Python 3.x
- NetworkX

Install NetworkX:

```bash
pip install networkx
```

## Usage

### 1. Standard VHDL Netlist

For a standalone VHDL netlist:

```bash
python levelizer.py -i "path\to\your_circuit.vhd"
```

### 2. VHDL Netlist with Custom Component Library

If the netlist uses components declared in an external VHDL package:

```bash
python levelizer.py -i "path\to\your_circuit.vhd" -p "path\to\Gates.vhdl"
```

### 3. Export Results to JSON

To save the levelization results to a JSON file:

```bash
python levelizer.py -i "path\to\your_circuit.vhd" -o "path\to\output.json"
```

## Command-Line Arguments

| Argument | Description | Required |
|---|---|---|
| `-i, --input` | Path to the main VHDL netlist (`.vhd`) | Yes |
| `-p, --pkg` | Path to the external VHDL package/library (`.vhdl`) | No |
| `-o, --output` | Path to save results as JSON | No |

> **Note:** Use `-p` only when your VHDL netlist depends on an external component library.
