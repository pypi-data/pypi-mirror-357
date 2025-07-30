# test_script.py
from method_flowchart import flowchart

class MyTestClass:
    def helper_a(self):
        """Helper A"""
        print("A")

    def helper_b(self):
        """Helper B"""
        self.helper_a()
        print("B")

    # @flowchart(output_file="my_test_flow.mmd")
    def main_method(self):
        """Main method docstring"""
        self.helper_b()
        print("Main")

def top_level_function():
    """Top level docstring"""
    print("Top")

# @flowchart()
def entry_point():
    """Entry point docstring"""
    top_level_function()
    obj = MyTestClass()
    obj.main_method()

if __name__ == "__main__":
    obj = MyTestClass()
    obj.main_method()
    entry_point()