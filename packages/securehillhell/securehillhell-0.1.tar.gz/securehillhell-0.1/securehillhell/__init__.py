def hill():
    return """# Static encryption matrix (must be invertible mod 26)
a = [
    [6, 24, 1],
    [13, 16, 10],
    [20, 17, 15]
]

# Static decryption matrix (modular inverse of 'a')
b = [
    [8, 5, 10],
    [21, 8, 21],
    [21, 12, 8]
]

# Plain text input (must be 3 uppercase letters)
msg = input("Enter 3-letter UPPERCASE text: ")

# Convert each character to a number (A=0, B=1, ..., Z=25)
plain = [ord(ch) - 65 for ch in msg]

# Encrypt
cipher = []
for i in range(3):
    total = 0
    for j in range(3):
        total += a[i][j] * plain[j]
    cipher.append(total % 26)

# Convert cipher numbers to letters
cipher_text = ''.join(chr(num + 65) for num in cipher)
print("Encrypted Text:", cipher_text)

# Decrypt
decrypted = []
for i in range(3):
    total = 0
    for j in range(3):
        total += b[i][j] * cipher[j]
    decrypted.append(total % 26)

# Convert decrypted numbers to letters
decrypted_text = ''.join(chr(num + 65) for num in decrypted)
print("Decrypted Text:", decrypted_text)
"""


def hell():
    return """# Simple power function to calculate (a^b) % mod
def power(a, b, mod):
    result = 1
    for _ in range(b):
        result = (result * a) % mod
    return result

# Input values
n = int(input("Enter value of n (modulus): "))
g = int(input("Enter value of g (base): "))

# Private keys
pr1 = int(input("Enter private key pr1 (Person 1): "))
pr2 = int(input("Enter private key pr2 (Person 2): "))

# Public keys
pu1 = power(g, pr1, n)  # pu1 = g^pr1 mod n
pu2 = power(g, pr2, n)  # pu2 = g^pr2 mod n

# Shared secret keys
key1 = power(pu2, pr1, n)  # Person 1: (pu2)^pr1 mod n
key2 = power(pu1, pr2, n)  # Person 2: (pu1)^pr2 mod n

# Output results
print("\nPublic key of Person 1 (pu1):", pu1)
print("Public key of Person 2 (pu2):", pu2)

print("\nSecret key computed by Person 1:", key1)
print("Secret key computed by Person 2:", key2)

if key1 == key2:
    print("\n Success! Shared secret key established.")
else:
    print("\n Error: Keys do not match.")
"""
