import matplotlib
import matplotlib.pyplot as plt

f = input("Absolute path to result file: ")

tlps  = open(f, "r").readlines()

fig, ax = plt.subplots()

for i in range(1,len(tlps)):
    a, b = tlps[i].replace('(', '').replace(')', '').replace('\n', '').split(',')
    a = int(a)
    b = float(b)
    ax.plot(a, b, 'o')
ax.set_title(f)
plt.show()
