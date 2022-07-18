from matplotlib import pyplot as plt

v = [ 3.8004, 3.8004, -2.544, -2.544, -2.544, -2.544 ]
t1 = 0.6
t2 = t1 + 0.256

t = [0, 0.1, 0.100001, 0.1 + t1, 0.1 + t2, 0.1 + t2 + 0.1 ]

plt.plot(t, v)
plt.plot([0.1 - 0.00005, 0.1 + 0.00005], [-0.4, 0.4])
plt.plot([0.1 + t1 - 0.00005, 0.1 + t1 + 0.00005], [-0.4, 0.4])
plt.plot([0.1 + t2 - 0.00005, 0.1 + t2 + 0.00005], [-0.4, 0.4])
plt.legend(["A recorded voltage", "First recorded disconnect", "Fifth recorded disconnect", "AIRs opened"])
plt.grid()
plt.show()
