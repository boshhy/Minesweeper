import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # The only time we know that the cells are mines is when the
        # count is the same as the number of cells left
        # Otherwise return an empty set
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # The only time we know that the cells are safe is when the
        # count is 0 (meaning no more mines)
        # Otherwise return an empty set
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Knowing that cell is a mine if it appears in self.cells
        # then remove that cell(mine) from self.cells and update count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Knowing that cell is safe, if it appears in self.cells
        # then remove that cell(mine) from self.cells
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        # Add the cell to the mines set
        self.mines.add(cell)
        # For every sentence in knowledge update the
        # sentence to mark the new cell(mine) as a mine
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        # Add the cell to the safes set
        self.safes.add(cell)
        # For every sentence in knowledge update the
        # sentence to mark the new cell(safe) as a safe
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2) Mark the cell as safe
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        # Take the location of the cell
        # and create an empty set for undetermined cells
        i, j = cell
        new_set = set()

        # For the cell go look at surrounding cells
        for r in range(i - 1, i + 2):
            for c in range(j - 1, j + 2):
                # Create a new cell for current currounding cell
                # We only want untracked cells so call it u_cell
                u_cell = (r, c)

                # Continue if u_cell is the original cell
                # or if the cell is already in safes
                if cell == u_cell or u_cell in self.safes:
                    continue

                # If already in mines update count
                # and continue to next cell
                if u_cell in self.mines:
                    count -= 1
                    continue

                # Make sure we don't go out of bounds this is for
                # the edge and corner cases, if everything checks out
                # add the set to 'new_set' of undetermined cells
                if 0 <= r < self.height and 0 <= c < self.width:
                    new_set.add(u_cell)

        # Create a new sentence using the new_set and the count
        new_sentence = Sentence(new_set, count)
        # Add the new sentence to knowledge base
        self.knowledge.append(new_sentence)

        # 4) mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        # We know that we have just added a new sentence so we have
        # to go mark any new mines and safe mines in our knowledge base
        # If we can determine a new mine or a safe mine we have to
        # update all sentences thay might contain the new mine or safes
        # This need to look at every sentence because a new mine or safes
        # will be subtracted from other sentences and we need to see if the
        # updated sentence will also return a set of mines or safes
        for sentence in self.knowledge:
            # If sentence return a non empty set for mines we need to mark them
            if sentence.known_mines():
                # For every cell in our returned mine set we need to mark it as a mine
                for cell in sentence.known_mines().copy():
                    self.mark_mine(cell)
            # If sentence return a non empty set for safes we need to mark them
            if sentence.known_safes():
                # For every cell in our returned safe set we need to mark it as a safe
                for cell in sentence.known_safes().copy():
                    self.mark_safe(cell)

        # 5) add any new sentences to the AI's knowledge base
        # if they can be inferred from existing knowledge
        # Now that we have some knowledge either from the clicked cell or
        # by the updated marked safes or maked mines from step 4,
        # we can see if we can create new sentences by seeing if the
        # new sentence created from the cell clicked is a subset of the other
        # sentences in out knowledge base. Keep in mind that step 4 might
        # have changed some sentences so we got to check every sentence
        for sentence in self.knowledge:
            # If new sentece is a subset of a sentence and we have some mines
            if new_sentence.cells.issubset(sentence.cells) and sentence.count > 0 and new_sentence != sentence:
                # Get the difference in sentences to create a new set(new_sub)
                new_sub = sentence.cells.difference(new_sentence.cells)
                # Create a new sentence using the new set(new_sub) and the difference in count
                current_sentence = Sentence(
                    list(new_sub), sentence.count - new_sentence.count)
                # If the newly created sentence is not in knowledge, then add it
                if current_sentence not in self.knowledge:
                    self.knowledge.append(current_sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Get all available safe moves
        moves = self.safes - self.moves_made
        # If the moves result is not empty then choose a random cell
        if moves:
            return random.choice(tuple(moves))
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Create an empty list for available moves
        moves = []
        # Go through all the cells in the game board
        for r in range(self.height):
            for c in range(self.width):
                # If the cell has not been played yet and it is not a mine
                # then we can append it to out available moves list
                if (r, c) not in self.moves_made and (r, c) not in self.mines:
                    moves.append((r, c))
        # If there is available moves to be made choose one at random
        if len(moves) != 0:
            return random.choice(moves)
        return None
