import argparse
import json
import os
import re
import networkx as nx


def parse_vhdl_package(pkg_file_path):
    """Parses a component declaration package file.

    Returns dict: { 'COMPONENT_NAME': {'in': [ports], 'out': [ports]} }
    """
    component_defs = {}
    with open(pkg_file_path, "r") as f:
        content = f.read()

    components = re.findall(
        r"component\s+(\w+)\s+is\s+port\s*\((.*?)\);\s*end\s+component;",
        content,
        re.DOTALL | re.IGNORECASE,
    )

    for comp_name, port_block in components:
        comp_name = comp_name.strip().upper()
        component_defs[comp_name] = {"in": [], "out": []}

        ports = port_block.split(";")
        for port in ports:
            match = re.search(r"([\w\s,]+):\s*(in|out)\s+", port, re.IGNORECASE)
            if match:
                signals = [
                    s.strip().upper() for s in match.group(1).split(",")
                ]
                direction = match.group(2).lower()
                component_defs[comp_name][direction].extend(signals)

    return component_defs


def parse_vhdl_netlist(netlist_file_path, component_defs=None):
    """Parses main VHDL netlist and maps Signal Drivers directly to Gate
    Instances."""
    primary_inputs = set()
    primary_outputs = set()

    # Track which gate instance drives which wire/signal
    signal_driver_gate = {}
    # Track which input wires/signals feed into which gate instance
    gate_input_signals = {}

    with open(netlist_file_path, "r") as f:
        content = f.read()

    # 1. Extract Primary Inputs and Outputs from Entity
    port_block = re.search(
        r"entity\s+.*?\s+is\s+port\s*\((.*?)\);",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if port_block:
        ports = port_block.group(1).split(";")
        for port in ports:
            match = re.search(r"([\w\s,]+):\s*(in|out)\s+", port, re.IGNORECASE)
            if match:
                signals = [s.strip() for s in match.group(1).split(",")]
                direction = match.group(2).lower()
                if direction == "in":
                    primary_inputs.update(signals)
                elif direction == "out":
                    primary_outputs.update(signals)

    DEFAULT_OUTPUT_PORTS = {"y", "z", "out", "q", "o"}

    # 2. Extract Gate Instances: e.g. g1: OR_2 port map (a, b, s1);
    instances = re.findall(
        r"(\w+)\s*:\s*(\w+)\s+port\s+map\s*\((.*?)\);",
        content,
        re.DOTALL | re.IGNORECASE,
    )

    for inst_name, gate_type, map_block in instances:
        inst_name = inst_name.strip()
        gate_type = gate_type.strip().upper()
        mappings = [m.strip() for m in map_block.split(",")]

        in_wires = []
        out_wires = []

        # Case A: Named Association (e.g., A => a, Y => s1)
        if any("=>" in m for m in mappings):
            known_out_ports = (
                set(component_defs[gate_type]["out"])
                if (component_defs and gate_type in component_defs)
                else DEFAULT_OUTPUT_PORTS
            )

            for m in mappings:
                if "=>" in m:
                    port, signal = [x.strip() for x in m.split("=>")]
                    if (
                        port.upper() in known_out_ports
                        or port.lower() in DEFAULT_OUTPUT_PORTS
                    ):
                        out_wires.append(signal)
                    else:
                        in_wires.append(signal)

        # Case B: Positional Association (e.g., a, b, s1)
        else:
            if component_defs and gate_type in component_defs:
                comp_in_cnt = len(component_defs[gate_type]["in"])
                in_wires = mappings[:comp_in_cnt]
                out_wires = mappings[comp_in_cnt:]
            else:
                # Default fallback: last signal is output
                in_wires = mappings[:-1]
                out_wires = [mappings[-1]]

        gate_input_signals[inst_name] = in_wires
        for out_wire in out_wires:
            signal_driver_gate[out_wire] = inst_name

    # Build Gate-to-Gate Direct Graph Connections
    gate_dependencies = {}
    for gate_inst, in_wires in gate_input_signals.items():
        driving_gates = set()
        for wire in in_wires:
            # If wire is driven by a previous gate, add that gate as a dependency
            if wire in signal_driver_gate:
                driving_gates.add(signal_driver_gate[wire])

        gate_dependencies[gate_inst] = list(driving_gates)

    return primary_inputs, primary_outputs, gate_dependencies


def compute_gate_levels(gate_dependencies):
    G = nx.DiGraph()

    for target_gate, driving_gates in gate_dependencies.items():
        G.add_node(target_gate)
        for driver in driving_gates:
            G.add_edge(driver, target_gate)

    gate_levels = {}

    try:
        topological_order = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        raise ValueError(
            "Error: Combinational feedback loop detected between gates!"
        )

    for gate in topological_order:
        predecessors = list(G.predecessors(gate))
        if not predecessors:
            # Gates taking only primary inputs start at Level 1
            gate_levels[gate] = 1
        else:
            # Level = max(driving gates levels) + 1
            gate_levels[gate] = max(gate_levels[p] for p in predecessors) + 1

    return gate_levels


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate gate node levels for any VHDL netlist."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to the main VHDL netlist file (.vhd)",
    )
    parser.add_argument(
        "-p",
        "--pkg",
        required=False,
        help="Path to the VHDL package/component definition file (optional)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        help="Path to save output JSON file (optional)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' does not exist.")
        exit(1)

    comp_defs = None
    if args.pkg and os.path.exists(args.pkg):
        print(f"Loading package definitions from: {args.pkg}")
        comp_defs = parse_vhdl_package(args.pkg)

    print(f"Parsing VHDL Netlist: {args.input}")
    pis, pos, gate_deps = parse_vhdl_netlist(args.input, comp_defs)

    results = compute_gate_levels(gate_deps)

    # Format result dictionary containing strictly gate nodes
    output_data = {
        "primary_inputs": sorted(list(pis)),
        "primary_outputs": sorted(list(pos)),
        "gate_node_levels": dict(
            sorted(results.items(), key=lambda item: item[1])
        ),
    }

    print("\n--- LEVELIZATION RESULTS ---")
    print(json.dumps(output_data, indent=4))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=4)
        print(f"\nResults successfully saved to: {args.output}")