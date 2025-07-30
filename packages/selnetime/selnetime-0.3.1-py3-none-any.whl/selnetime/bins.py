import numpy as np

class Bin:
    def __init__(self, n: int):
        """
        Class that handles the creation of intervals, their middle points, couples, left and right components.

        Parameters:
        - nb_bin: The number of bins or intervals.

        The class initializes the attributes for working with intervals, including their start and end points,
        middle points, and couples (pairs of left and right endpoints).
        """
        self.nb_bin = n
        debut, fin = 0, 1
        self.points = np.linspace(debut, fin, self.nb_bin + 1)
        self.left = self.points[:-1]
        self.right = self.points[1:]
        self.middle = np.zeros(self.nb_bin)
        self.middle[1:-1] = 0.5 * (self.left[1:-1] + self.right[1:-1])
        self.middle[-1] = 1
        self.couple = np.asarray(
            [(0, 0)] + list(zip(self.left[1:-1], self.right[1:-1])) + [(1, 1)]
        )
