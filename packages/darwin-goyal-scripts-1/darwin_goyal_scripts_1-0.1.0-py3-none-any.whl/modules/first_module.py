print("This line appears outside any method and hence would be printed first after it has been interpreted")

def print_hello_world():
    print("Hello World")

    # __name__ is a special variable that contains the name of the module when imported
    # and __main__ when run as a script
    print(__name__)


if __name__ == "__main__":
    print("main method is executed automatically")
    print_hello_world()