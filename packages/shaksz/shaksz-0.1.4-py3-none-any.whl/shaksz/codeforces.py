
def _4a(input_data): # Codeforces Problem 4A: Watermelon
    """
    This function checks if a given integer is an even number greater than 2.
    If it is, it returns "Yes", otherwise it returns "No".
    """
    # input_data is expected to be a string representing an integer
    # Convert input_data to an integer
    # For example, if input_data is "4", it will be converted to 4
    # If input_data is "3", it will be converted to 3

    s = input_data # Read input data as a string input()
    s = int(s)
    if s %2 == 0 and s != 2:
        print("Yes")
        return "Yes"    # no need to return in active codeforces problems, but it's good practice for testing
    else:
        print("No")
        return "No"     # no need to return in active codeforces problems, but it's good practice for testing