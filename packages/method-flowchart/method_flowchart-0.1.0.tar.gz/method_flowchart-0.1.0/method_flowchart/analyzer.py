import ast
import inspect
import sys

class MethodAnalyzer:
    def __init__(self, target_method):
        # If the initially targeted method is a decorated function,
        # we want to start analysis from its original, unwrapped version.
        if hasattr(target_method, '__wrapped__'):
            self.target_method = target_method.__wrapped__
        else:
            self.target_method = target_method
            
        # Get the module of the (potentially unwrapped) target method
        self.module = sys.modules[self.target_method.__module__]
        # Get the source code of the entire module for AST parsing.
        # This is crucial to find all functions and methods, including class methods.
        self.module_source = inspect.getsource(self.module)
        self.tree = ast.parse(self.module_source)
        self.call_graph = {}
        self.method_docstrings = {}
        # `processed_methods` stores names of methods whose *original* bodies have been analyzed
        self.processed_methods = set()

    def _resolve_callable_in_module(self, name):
        """
        Attempts to find a callable (function or method) with the given name
        within the target module's top-level or its defined classes.
        """
        # 1. Check top-level functions in the module
        obj = getattr(self.module, name, None)
        if inspect.isfunction(obj) or inspect.ismethod(obj): # `ismethod` for unbound class methods
            return obj

        # 2. Check methods within classes defined in the module
        for attr_name in dir(self.module):
            attr_value = getattr(self.module, attr_name)
            if inspect.isclass(attr_value):
                method = getattr(attr_value, name, None)
                if inspect.isfunction(method) or inspect.ismethod(method):
                    # Found a method. If multiple classes have a method with the same name,
                    # this will return the first one found.
                    return method
        return None

    def _find_method_node(self, method_name):
        """Finds the AST node for a method/function by its name within the module's AST."""
        for node in ast.walk(self.tree):
            # Ensure we're finding the AST node for the *original* method's name
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
                docstring = ast.get_docstring(node)
                self.method_docstrings[method_name] = docstring if docstring else ""
                return node
        return None
    
    def _analyze_node_for_calls(self, node, current_method_name):
        self.processed_methods.add(current_method_name)

        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Call):
                called_name = None
                
                # Case 1: Direct function call (e.g., `func()`)
                if isinstance(sub_node.func, ast.Name):
                    called_name = sub_node.func.id
                # Case 2: Attribute call (e.g., `obj.method()`, `self.method()`)
                elif isinstance(sub_node.func, ast.Attribute):
                    called_name = sub_node.func.attr
                    
                if called_name and called_name not in self.call_graph.get(current_method_name, []):
                    # Removed: if called_name == "flowchart": continue
                    # This filter is no longer necessary as unwrapping should prevent it from being seen.

                    # Add the call to the current method's call list in the graph
                    self.call_graph.setdefault(current_method_name, set()).add(called_name)

                    # Attempt to get the actual callable object for recursive analysis
                    callable_obj = self._resolve_callable_in_module(called_name)

                    if callable_obj:
                        # Determine the actual function object to analyze (unwrapped if it's a decorator wrapper)
                        function_to_analyze = callable_obj
                        if hasattr(callable_obj, '__wrapped__'):
                            function_to_analyze = callable_obj.__wrapped__

                        # Ensure it's a function/method and belongs to the current module (or its classes)
                        if (inspect.isfunction(function_to_analyze) or inspect.ismethod(function_to_analyze)):
                        # and function_to_analyze.__module__ == self.module.__name__:
                            
                            # Recursively analyze if its *unwrapped name* hasn't been processed yet
                            if function_to_analyze.__name__ not in self.processed_methods:
                                self._analyze_method_recursively(function_to_analyze)

    def _analyze_method_recursively(self, method_obj):
        # `method_obj` here is already the unwrapped function/method if it was a decorator wrapper
        method_name = method_obj.__name__
        
        # If this method's AST has already been processed for calls in the current graph, skip
        if method_name in self.processed_methods:
            return
        
        # Find the AST node for this method by its name within the module's parsed tree
        method_node = self._find_method_node(method_name)
        
        if method_node:
            # If the node is found, proceed to analyze its internal calls
            self._analyze_node_for_calls(method_node, method_name)

    def build_call_graph(self):
        """Builds the complete call graph starting from the target method."""
        self._analyze_method_recursively(self.target_method)
        return self.call_graph, self.method_docstrings