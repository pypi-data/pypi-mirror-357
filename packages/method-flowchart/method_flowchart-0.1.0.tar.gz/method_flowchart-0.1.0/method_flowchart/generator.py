import inspect

class MermaidGenerator:
    def __init__(self, call_graph, method_docstrings):
        self.call_graph = call_graph
        self.method_docstrings = method_docstrings
        self.mermaid_lines = []
        self.defined_nodes = set() # To keep track of all unique nodes explicitly defined
        self.external_calls = set() # To identify calls that are not internal methods

    def generate_flowchart(self):
        self.mermaid_lines.append("graph TD")

        # --- Phase 1: Identify all unique nodes and their types (internal/external) ---
        all_methods_involved = set(self.method_docstrings.keys())
        for caller, callees in self.call_graph.items():
            all_methods_involved.add(caller)
            for callee in callees:
                # Exclude 'flowchart' from being treated as a callable or node
                if callee == "flowchart":
                    continue

                # If a callee is not one of our internally analyzed methods,
                # it's likely an external call (like 'print')
                if callee not in self.method_docstrings:
                    self.external_calls.add(callee)
                else:
                    all_methods_involved.add(callee)


        # --- Phase 2: Define all nodes explicitly ---
        # First, internal methods with docstrings (using [] for rectangular nodes and label)
        for method_name in sorted(all_methods_involved): # Sorting for consistent output
            if method_name in self.method_docstrings: # It's an internal method with a docstring
                docstring = self.method_docstrings.get(method_name, "").replace('\n', '<br/>')
                # Use asterisks (*) to make the docstring italic
                self.mermaid_lines.append(f'    {method_name}[{method_name}<br/>*{docstring}*]')
                self.defined_nodes.add(method_name)
            
        # Then, external calls (like 'print') using [""] for node definition and label
        for external_call in sorted(self.external_calls):
            self.mermaid_lines.append(f'    {external_call}["{external_call}"]')
            self.defined_nodes.add(external_call)

        # --- Phase 3: Create subgraphs for methods that make calls ---
        for caller, callees in self.call_graph.items():
            filtered_callees = [callee for callee in callees if callee != "flowchart"] # Filter out 'flowchart'
            
            if filtered_callees: # Only create a subgraph if the method has actual calls within it
                subgraph_id = f"{caller}_flow"
                self.mermaid_lines.append(f"    subgraph {subgraph_id} [Flow of {caller}]")
                
                # Add nodes to the subgraph, ensuring the caller itself is included
                self.mermaid_lines.append(f"        {caller}")

                for callee in sorted(filtered_callees):
                    if callee in self.defined_nodes: # Only add if it's a node we've defined
                        self.mermaid_lines.append(f"        {callee}")
                self.mermaid_lines.append("    end")

        # --- Phase 4: Add the edges (calls) ---
        for caller, callees in self.call_graph.items():
            for callee in sorted(callees):
                if callee == "flowchart": # Skip edges involving 'flowchart'
                    continue

                self.mermaid_lines.append(f"    {caller} --> {callee}")

        return "\n".join(self.mermaid_lines)