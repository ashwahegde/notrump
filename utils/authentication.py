import random
def generate_otp(n=9):
    return random.randint(10**n,10**(n+1)-1)
