from math import pi

def get_LCG_report(nums, m, a, c, seed, period, pi_est):
    txt = "LCG Parameters:\n"
    txt += f"m = {m} \na = {a} \nc = {c} \nseed = {seed}\n\n"
    txt += f"Generated numbers: {len(nums)}\n"
    txt += f"Period: {period}\n\n"
    txt += "Cesaro Test Results:\n"
    txt += f"Estimated pi = {pi_est}\n"
    txt += f"Absolute error = {abs(pi - pi_est)}\n\n"
    txt += "Generated Sequence:\n"
    for i, num in enumerate(nums):
        txt += f"{i+1}: {num}\n"
    return txt
    