import json
import requests

site = "https://api.npoint.io/2b57052af2060e84dc86"

# Write the functions convert_number and replace_number here
# Follow the logic below.

# Trying to load JSON into text
r = requests.get(site)
print(r.json())
text = r.json()['users']

# Debug 
for i in text: 
    print("parse " + str(i))

def convert_number(text):
    numbers = []
    for user in text:
        for item in user:
            if item.isdigit():
                numbers.append(int(item))
    return numbers

def replace_number(number_list, being_replace, to_replace):
    # Replace all the number in the list
    for i in range(len(number_list)):
        if number_list[i] == being_replace:
            number_list[i] = to_replace
    return number_list

# call the function convert_number
# convert all elements (except the first one) into number and return it as a list
y = convert_number(text[0])
print("y")
print(y)

# call the function replace_number
# replace all number 1 by the number 10 in the function
z = replace_number(number_list = y, being_replace = 1, to_replace = 10)
print("z")
print(z)

sum = 0
for i in z:
    sum = sum + i
    print("sum = " + str(sum) + "; i =" + str(i))

print("Total = " + str(sum))