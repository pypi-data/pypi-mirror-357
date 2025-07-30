import inspect
import os
from typing import Optional
from .analyzer import MethodAnalyzer
from .generator import MermaidGenerator
# No import for decorated_methods_registry

def flowchart(output_file: Optional[str] = None):
    """
    Decorator to generate a Mermaid flowchart for the decorated method's call graph.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Instantiate MethodAnalyzer without any registry
            analyzer = MethodAnalyzer(func)
            call_graph, method_docstrings = analyzer.build_call_graph()

            generator = MermaidGenerator(call_graph, method_docstrings)
            mermaid_code = generator.generate_flowchart()

            out_file = output_file if output_file is not None else f"{func.__name__}_flow.mmd"

            with open(out_file, "w") as f:
                f.write(mermaid_code)
            print(f"Mermaid flowchart saved to {out_file}")

            return func(*args, **kwargs)
        return wrapper
    return decorator