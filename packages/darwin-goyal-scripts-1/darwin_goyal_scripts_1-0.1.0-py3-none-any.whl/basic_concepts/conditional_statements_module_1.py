def demonstrate_conditional_statement():
    if ("__name__" == "__main__"):
        print("This line appears only when this module is run as a script")
    else:
        print("This line appears only when this module is imported")

if __name__ == "__main__":
    demonstrate_conditional_statement()