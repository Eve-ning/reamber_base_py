from reamber.algorithms.plot.nps import npsPlot
from reamber.osu.OsuMap import OsuMap
import matplotlib.pyplot as plt

m = OsuMap()
m.readFile("note/PLANETSHAPER.osu")
npsPlot(m, binSize=500)
plt.show()