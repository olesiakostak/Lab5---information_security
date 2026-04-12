class LCG:
    def __init__(self, m: int, a: int, c: int, seed: int):
        self.m, self.a, self.c, self.seed = m, a, c, seed

    def generate(self, count: int) -> list[int]:
        gen_nums = []
        x_prev = self.seed

        for n in range(count):
            x_cur = (self.a * x_prev + self.c) % self.m
            x_prev = x_cur
            gen_nums.append(x_prev)

        return gen_nums

    def calculatePeriod(self, count: int) -> int:
        period = 0
        x_prev = self.seed

        for _ in range(count):
            x_cur = (self.a * x_prev + self.c) % self.m
            x_prev = x_cur
            period += 1
            if x_cur == self.seed: return period

        return -1
