import os
import pytest
from method_flowchart.analyzer import MethodAnalyzer
from method_flowchart.generator import MermaidGenerator
from method_flowchart.decorator import flowchart

# Sample functions/classes for testing
def sample_func():
    """Sample function docstring"""
    print("Hello")

class SampleClass:
    def method_a(self):
        """Method A docstring"""
        self.method_b()
    def method_b(self):
        """Method B docstring"""
        pass

class Engine:
    def __init__(self):
        self.oil_level = 100  # Assume oil level is a percentage


    def start(self):
        print("Engine started.")
        check_oil_response = self.check_oil()
        return check_oil_response

    def check_oil(self) -> bool:
        print("Checking oil level.")
        if self.oil_level > 20:
            print("Oil level is sufficient.")
            return True
        else:
            print("Oil level is too low!")
            return False

class Transmission:
    def engage(self):
        print("Transmission engaged.")
        return True

class Car:
    def __init__(self):
        self.engine = Engine()
        self.transmission = Transmission()

    def drive(self):
        if self.engine.start():
            if self.transmission.engage():
                print("Car is now driving.")
                return True
        print("Car failed to drive.")
        return False

class Driver:
    def __init__(self, name):
        self.name = name
        self.car = Car()

    def go_to_work(self):
        print(f"{self.name} is attempting to go to work.")
        success = self.car.drive()
        if success:
            print(f"{self.name} arrived at work.")
        else:
            print(f"{self.name} could not get to work.")

# Example usage
if __name__ == "__main__":
    driver = Driver("Alice")