import string

def evaluate(password):
    basepoints = len(password)
    regpoints = 0
    symbols = string.punctuation

    for char in password:
        if char.islower():
            regpoints += 3
        if char.isupper():
            regpoints += 5
        if char.isdigit():
            regpoints += 7
        if char in symbols:
            regpoints += 10

    variance = 0
    for i in range(len(password) - 1):
        c1, c2 = password[i], password[i + 1]

        if c1.islower():
            if c2.islower():
                variance += 1
            elif c2.isupper():
                variance += 2
            elif c2.isdigit():
                variance += 5
            else:
                variance += 10

        elif c1.isupper():
            if c2.islower():
                variance += 2
            elif c2.isupper():
                variance += 1
            elif c2.isdigit():
                variance += 2
            else:
                variance += 5

        elif c1.isdigit():
            if c2.islower():
                variance += 5
            elif c2.isupper():
                variance += 2
            elif c2.isdigit():
                variance += 1
            else:
                variance += 2

        else:
            if c2.islower():
                variance += 10
            elif c2.isupper():
                variance += 5
            elif c2.isdigit():
                variance += 2
            else:
                variance += 1

    score = variance * (basepoints + regpoints)
    return score

def rate(score):
    if score < 500:
        return "🔴 Very Weak"
    elif score < 1000:
        return "🟠 Weak"
    elif score < 1250:
        return "🟡 Moderate"
    elif score < 3500:
        return "🟢 Strong"
    else:
        return "🟣 Very Strong"
