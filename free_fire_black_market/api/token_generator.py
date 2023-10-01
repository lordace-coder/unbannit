import random


def generate_token(count = 4):
    my_list = ['1','2','3','4','5','6','7','8','9','0','a','b','c','d','e']
    token_list = random.choices(my_list,k=count)
    token = ''
    for i in token_list:
        token+=i
    return token

