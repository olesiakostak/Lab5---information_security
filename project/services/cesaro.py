from math import pi

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def cesaro_test(nums):
    count = 0
    l = len(nums) 
    if l < 2: 
        return 0.0, 100.0
    pairs_num = l // 2
    
    for i in range(0, pairs_num*2, 2):
        if gcd(nums[i], nums[i+1]) == 1:
            count += 1

    if count == 0:
        return 0.0, 100.0

    prob = count / pairs_num 
    calc_pi = (6 / prob) ** 0.5
    error = abs(pi - calc_pi)
    return calc_pi, error


