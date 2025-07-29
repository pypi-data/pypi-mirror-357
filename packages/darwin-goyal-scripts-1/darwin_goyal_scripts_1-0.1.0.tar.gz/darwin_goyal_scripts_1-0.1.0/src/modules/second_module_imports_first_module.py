import first_module
import sys
from first_module import print_hello_world

# __name__ is a special variable that contains the name of the module when imported
# and __main__ when run as a script. Below method call will demonstrate this. From Terminal,
# we will call python3 second_module_imports_first_module.py
if __name__ == "__main__":
    print_hello_world()
    print(first_module.__file__)
    print(sys.path)
    print(sys.__file__)