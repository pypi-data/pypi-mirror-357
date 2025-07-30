# Method Flowchart

Generate Mermaid flowcharts from Python methods or class methods via a command-line interface.

## Installation

Install the package (from source):

```bash
pip install .
```

## Usage (CLI)

After installation, use the CLI tool `method-flowchart`:

```bash
method-flowchart <python_file> <function_or_Class.method> [-o output_file]
```

- `<python_file>`: Path to the Python file containing the function or class method you want to analyze.
- `<function_or_Class.method>`: Name of the function (e.g., `my_function`) or class method (e.g., `MyClass.my_method`).
- `-o, --output`: (Optional) Output file for the Mermaid diagram. Defaults to `<function_or_Class.method>_flow.mmd`.

### Example

Suppose you have a file `example.py`:

```python
def foo():
    bar()
    print("Hello")

def bar():
    pass
```

To generate a flowchart for `foo`:

```bash
method-flowchart example.py foo -o foo_flow.mmd
```

To generate a flowchart for a class method:

```bash
method-flowchart example.py MyClass.my_method -o my_method_flow.mmd
```

The output will be a Mermaid diagram file you can visualize with Mermaid tools.

## Notes
- The CLI dynamically imports the specified file, so ensure it is importable and does not have side effects on import.
- The decorator-based API is deprecated in favor of the CLI.
