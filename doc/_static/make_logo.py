import matplotlib.pyplot as plt
from numpy import meshgrid, linspace

fig, ax = plt.subplots(figsize=(27, 9))
x, y = meshgrid((0, 100), linspace(0, 0.1, 1000))
ax.contourf(x, y, y, cmap=plt.get_cmap("seismic_r"), levels=linspace(0, 0.1, 1000))
ax.set_yticks([])
ax.set_axis_off()

fig.savefig("bg.png", dpi=1200, bbox_inches="tight", pad_inches=0)
