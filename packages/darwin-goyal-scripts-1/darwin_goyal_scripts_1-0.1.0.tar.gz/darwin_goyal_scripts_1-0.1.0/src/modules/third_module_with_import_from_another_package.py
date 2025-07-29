# from ../../../basic_concepts/for_loop_module_1 import print_1_to_10
# from ...basic_concepts.src.for_loop_module_1 import print_1_to_10

from basic_concepts.src import for_loop_module_1
import sys

if __name__ == "__main__":
    for_loop_module_1.print_1_to_10()
    print(sys.path)