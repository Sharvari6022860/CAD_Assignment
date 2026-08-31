              VHDL NETLIST LEVELIZER - USAGE INSTRUCTIONS
DESCRIPTION:
  This script computes topological gate-level depths for VHDL netlists.
  It supports both custom external packages (component libraries) and 
  standalone standard VHDL netlists.

------------------------------------------------------------------------
1. PREREQUISITES
------------------------------------------------------------------------
  - Python 3.x installed on your system.
  - Required Python packages: networkx

  To install the required library, run the following command in terminal:
      pip install networkx

------------------------------------------------------------------------
2. HOW TO RUN THE SCRIPT
------------------------------------------------------------------------

  OPTION A: Standard VHDL (Without external component package)
  ------------------------------------------------------------
  Use this mode if your VHDL netlist contains standard gates or does not
  depend on external component declarations:

      python levelizer.py -i "path\to\your_circuit.vhd"

  OPTION B: Custom VHDL Package (With external component library)
  ---------------------------------------------------------------
  Use this mode if your VHDL code uses custom gates declared inside a 
  separate VHDL package file (e.g., Gates.vhdl):

      python levelizer.py -i "path\to\your_circuit.vhd" -p "path\to\Gates.vhdl"

  OPTION C: Export Results to JSON File
  -------------------------------------
  Append the -o flag to save the levelization output directly into a JSON file:

      python levelizer.py -i "path\to\your_circuit.vhd" -o "path\to\output.json"

------------------------------------------------------------------------
3. COMMAND-LINE ARGUMENTS SUMMARY
------------------------------------------------------------------------
  -i, --input   : (Required) Path to the main VHDL netlist file (.vhd).
  -p, --pkg     : (Optional) Path to the VHDL component library file (.vhdl).
  -o, --output  : (Optional) Path to save output data to a JSON file.

========================================================================
