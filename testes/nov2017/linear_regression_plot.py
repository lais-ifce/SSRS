import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from os import path as ospath

def split(path):
    x = []
    y = []
    if ospath.exists(path):
        with open(path) as f:
            content = f.readlines()
            for i in range(0, len(content)):
                a, b = content[i].replace('(', '').replace(')', '').replace('\n', '').split(',')
                x.append(float(a))
                y.append(float(b))
    return np.asarray(x), np.asarray(y)

if __name__ == "__main__":
    path = input("Path to result file: ")
    x, y = split(path)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    print("Slope: {}\nIntercept: {}\nr_value: {}\np_value: {}\nerr {}".format(slope, intercept, r_value, p_value, std_err))
    plt.plot(x, y, 'o', label='original data')
    plt.plot(x, intercept + slope*x, 'r', label='fitted line')
    plt.legend()
    plt.title(path)
    plt.show()
