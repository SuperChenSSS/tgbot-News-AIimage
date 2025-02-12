def reverse_string(s):
    reversed_str = ""
    for char in s:
        reversed_str = char + reversed_str
    return reversed_str

# Invoke the resverse string function
def main():
    s = "Hello, World!"
    print(reverse_string(s))

if __name__ == '__main__':
    main()