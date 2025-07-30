class helper_module:
    def __init__(self):
        """
        This will implement after completion
        """
        pass
    def find_symbol_pos(self,symbol_id, grid):    
        """
        This method finds the symbol_id position(s) on the grid

        :param symbol_id: index of the symbol for which the position to be found
        :param grid: symbol grid passed in 2D list
        :return: list: position of the passed symbol id in passed symbol grid
        """

        symbol_grid = [symbol for row in grid for symbol in row]
        pos = [count for count, symbol in enumerate(symbol_grid) if symbol == symbol_id]

        return pos