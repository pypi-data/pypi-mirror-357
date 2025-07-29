from typing import List, Optional, Tuple, Dict
from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
from itertools import product

class Keys:
    """
    Represents a layout of keys, typically for a keypad or keyboard.

    Attributes
    ----------
    keys : List[List[str]]
        A 2D list representing the keys in each row.
    row_offset : Optional[List[int]]
        Optional list specifying the horizontal offset for each row.
        If None, defaults to no offset for any row.
    positions : OrderedDict[str, Tuple[int, int]]
        An ordered dictionary mapping each key to its (x, y) position.
    distances : OrderedDict[Tuple[str, str], float]
        An ordered dictionary mapping pairs of keys to the Euclidean distance
        between their positions.
    vectors : OrderedDict[Tuple[str, str], np.ndarray]
        An ordered dictionary mapping pairs of keys to the vector sum of their
        positions.
    """
    def __init__(self, keys: List[List[str]], row_offset: Optional[List[int]] = None) -> None:
        """
        Initializes the Keys object with the key layout and optional row offsets.

        Parameters
        ----------
        keys : List[List[str]]
            A 2D list representing the keys in each row.
        row_offset : Optional[List[int]], optional
            Optional list specifying the horizontal offset for each row.
            If provided, its length must match the number of rows in `keys`.
            Defaults to None.

        Raises
        ------
        ValueError
            If `row_offset` is provided and its length does not match the
            number of rows in `keys`.
        """
        self.keys: List[List[str]] = keys

        if row_offset:
            if len(row_offset) != len(keys):
                raise ValueError("Length of row_offset must match the number of rows in keys.")
            self.row_offset: np.ndarray = np.cumsum(row_offset)
        else:
            self.row_offset: List[int] = [0] * len(keys)

        self.positions: OrderedDict[str, Tuple[int, int]] = OrderedDict()
        self.distances: OrderedDict[Tuple[str, str], float] = OrderedDict()
        self.vectors: OrderedDict[Tuple[str, str], np.ndarray] = OrderedDict()

        self._get_positions()
        self._get_distances()
        self._get_vectors()

    def _get_positions(self) -> None:
        """
        Calculates the (x, y) position for each key based on its row and column
        index and the row offsets. Stores the results in the `self.positions`
        attribute.
        """
        for i, row in enumerate(self.keys):
            for j, key in enumerate(row):
                self.positions[key] = float(j + self.row_offset[i]), float(-i)

    def _get_distances(self) -> None:
        """
        Calculates the Euclidean distance between the positions of all pairs of
        keys. Stores the results in the `self.distances` attribute.
        """
        for key1, key2 in product(self.positions.keys(), repeat=2):
            self.distances[(key1, key2)] = np.linalg.norm(
                self._subtract_keys(self.positions[key1], self.positions[key2])
            )

    def _get_vectors(self) -> None:
        """
        Calculates the vector sum of the positions of all pairs of keys.
        Stores the results in the `self.vectors` attribute.
        """
        for key1, key2 in product(self.positions.keys(), repeat=2):
            self.vectors[(key1, key2)] = tuple(np.array(
                self.positions[key1]) + np.array(self.positions[key2]
            ))

    def plot_keys(self) -> plt.Figure:
        """
        Plots the layout of the keys.

        Returns
        -------
        matplotlib.figure.Figure
            The matplotlib Figure object containing the plot.
        """
        fig: plt.Figure = plt.gcf()

        for k, v in self.positions.items():
            # plt.plot to adjust keypad size. plotting one point at a time it
            # doesn't actually plot anything.
            plt.plot(*v)
            plt.text(*v, k, ha='center', va='center')
        plt.axis('off')

        return fig

    def plot_entry(self, entry: str, arrow_props: Optional[Dict] = None) -> plt.Figure:
        """
        Plots a sequence of key presses (an "entry") on the key layout, drawing
        arrows between consecutive keys.

        Parameters
        ----------
        entry : str
            A string representing the sequence of key presses. Each character
            in the string must correspond to a key in the layout.
        arrow_props : Optional[Dict], optional
            A dictionary of keyword arguments to pass to `plt.annotate` for
            styling the arrows. Defaults to an empty dictionary.

        Returns
        -------
        matplotlib.figure.Figure
            The matplotlib Figure object containing the plot.
        """
        fig: plt.Figure = self.plot_keys()

        custom_arrow_props: Dict = dict(
            arrowstyle='-|>',
            connectionstyle="arc3,rad=.1",
        )

        if arrow_props:
            custom_arrow_props.update(arrow_props)

        for i in range(len(entry) - 1):
            start: Tuple[int, int] = self.positions[entry[i]]
            end: Tuple[int, int] = self.positions[entry[i+1]]

            plt.annotate(text='', xy=end, xytext=start, arrowprops=custom_arrow_props)

        return fig

    def _add_keys(self, key1: Tuple[int, ...], key2: Tuple[int, ...]) -> Tuple[int, ...]:
        """
        Adds corresponding elements of two key tuples.

        Parameters
        ----------
        key1 : Tuple[int, ...]
            The first key tuple.
        key2 : Tuple[int, ...]
            The second key tuple.

        Returns
        -------
        Tuple[int, ...]
            A tuple containing the element-wise sum of `key1` and `key2`.
        """
        added_up: List[int] = []
        for i, j in zip(key1, key2):
            added_up.append(i + j)

        return tuple(added_up)

    def _subtract_keys(self, key1: Tuple[int, ...], key2: Tuple[int, ...]) -> Tuple[int, ...]:
        """
        Subtracts corresponding elements of the second key tuple from the first.

        Parameters
        ----------
        key1 : Tuple[int, ...]
            The first key tuple.
        key2 : Tuple[int, ...]
            The second key tuple.

        Returns
        -------
        Tuple[int, ...]
            A tuple containing the element-wise difference of `key1` and `key2`.
        """
        subtracted: List[int] = []
        for i, j in zip(key1, key2):
            subtracted.append(i - j)

        return tuple(subtracted)

    def _get_sequential_vectors(self, entry: str) -> list:
        """
        Calculates the vector sum of the positions of all pairs of keys in the
        given entry.

        Parameters
        ----------
        entry : str

        Returns
        -------
        np.ndarray
            A 2D array representing the vector sum of the positions of all pairs
            of keys in the given entry.
        """
        vectors: List[np.ndarray] = []

        for i in range(len(entry) - 1):
            x = self.positions[entry[i]]
            y = self.positions[entry[i+1]]
            vectors.append(self._subtract_keys(y, x))

        return vectors

    def _get_bounds(self, entry: str) -> Tuple[int, int, int, int]:
        sequence_positions = self._get_positions(entry)
        x = [coord[0] for coord in sequence_positions]
        y = [coord[1] for coord in sequence_positions]
        return min(x), max(x), min(y), max(y)

    def _get_vector_bounds(self, entry: str) -> Tuple[int, int, int, int]:
        sequence_positions = self._get_sequential_vectors(entry)
        x = [coord[0] for coord in sequence_positions]
        y = [coord[1] for coord in sequence_positions]
        return min(x), max(x), min(y), max(y)