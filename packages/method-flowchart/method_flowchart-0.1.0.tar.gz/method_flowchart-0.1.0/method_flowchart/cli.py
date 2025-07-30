import argparse
import importlib.util
import os
import sys
from method_flowchart.analyzer import MethodAnalyzer
from method_flowchart.generator import MermaidGenerator

def import_module_from_path(module_path):
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def get_callable(module, func_path):
    if "." in func_path:
        class_name, method_name = func_path.split(".", 1)
        cls = getattr(module, class_name, None)
        if cls is None:
            raise AttributeError(f"Class '{class_name}' not found in module.")
        func = getattr(cls, method_name, None)
        if func is None:
            raise AttributeError(f"Method '{method_name}' not found in class '{class_name}'.")
        return func
    else:
        func = getattr(module, func_path, None)
        if func is None:
            raise AttributeError(f"Function '{func_path}' not found in module.")
        return func

def main():
    parser = argparse.ArgumentParser(description="Generate Mermaid flowcharts from Python methods.")
    parser.add_argument("file", help="Path to the Python file to analyze.")
    parser.add_argument("function", help="Function or Class.method to analyze.")
    parser.add_argument("-o", "--output", help="Output file for the Mermaid diagram.", default=None)
    args = parser.parse_args()

    module = import_module_from_path(args.file)
    func = get_callable(module, args.function)

    analyzer = MethodAnalyzer(func)
    call_graph, method_docstrings = analyzer.build_call_graph()
    generator = MermaidGenerator(call_graph, method_docstrings)
    mermaid_code = generator.generate_flowchart()

    output_file = args.output or f"{args.function.replace('.', '_')}_flow.mmd"
    with open(output_file, "w") as f:
        f.write(mermaid_code)
    print(f"Mermaid flowchart saved to {output_file}")

if __name__ == "__main__":
    main() 