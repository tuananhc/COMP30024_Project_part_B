import math
import random
import copy

from ANZ.utils import *
from referee.board import Board

class Node:
    def __init__(self, move, color, board):
        self.board = board
        self.move = move
        self.value = None
        self.color = color
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class Player:
    def __init__(self, player, n):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "red" if your player will
        play as Red, or the string "blue" if your player will play
        as Blue.
        """
        # put your code here
        self.board = Board(n)
        self.color = player
        self.count = 0
        if n < 6:
            self.DEPTH = 3
        elif n < 10:
            self.DEPTH = 2
        else:
            self.DEPTH = 1
        self.node = None

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        # put your code here
        if self.count == 0 and self.color == "red":
            # First move can be random as long as it is not the acute corners or the middle hex
            i = random.randint(0, self.board.n - 1)
            j = random.randint(0, self.board.n - 1)
            while (i, j) == (0, 0) or (i, j) == (self.board.n - 1, self.board.n - 1) or (i, j) == (math.floor(self.board.n / 2), math.floor(self.board.n / 2)):
                i = random.randint(0, self.board.n - 1)
                j = random.randint(0, self.board.n - 1)
            return ("PLACE", i, j)

        # Check if blue should steal red's move. Blue generally should steal red's move unless red first move is in the acute 
        # corners or among the red border, except for the obtuse corners
        elif self.count == 1 and self.color == "blue":
            found = False
            for i in range(self.board.n):
                for j in range(self.board.n):
                    if self.board[(i, j)] == "red":
                        found = True
                        break
                if found: break
            
            # Check corners
            if not ((i == 0 and j == 0) or (i == self.board.n - 1 and j == self.board.n - 1)):
                return ("STEAL", )
            else:
                return ("PLACE", math.floor(self.board.n / 2), math.floor(self.board.n / 2))

        # For subsequent moves, use Minimax with alpha beta pruning and terminate depth to find the optimal move
        tree = self.construct_tree()
        best_value = self.minimax(tree, -math.inf, math.inf)

        for child in tree.children:
            if child.value == best_value:
                self.node = child 
                return ("PLACE", child.move[0], child.move[1])
    
    def turn(self, player, action):
        """
        Called at the end of each player's turn to inform this player of 
        their chosen action. Update your internal representation of the 
        game state based on this. The parameter action is the chosen 
        action itself. 
        
        Note: At the end of your player's turn, the action parameter is
        the same as what your player returned from the action method
        above. However, the referee has validated it at this point.
        """
        
        # put your code here
        if action[0] == "PLACE":
            self.board.place(player, (action[1], action[2]))
        else:
            self.board.swap()
        self.count += 1

    def construct_tree(self):
        root = Node(None, self.color, self.board)
        is_red = self.color == "red"
        possibles = []
        for i in range(self.DEPTH):
            possibles.append([])
            if i == 0:
                visited = defaultdict(bool)
                for j in range(root.board.n):
                    for k in range(root.board.n):
                        if root.board[(j, k)]:
                            for neighbour1 in root.board._coord_neighbours((j, k)):
                                # for neighbour2 in root.board._coord_neighbours(neighbour1):
                                    neighbour1 = (int(neighbour1[0]), int(neighbour1[1]))
                                    if not visited[neighbour1] and not root.board[neighbour1]:
                                        if is_red:
                                            color = "red"
                                        else:
                                            color = "blue"
                                        new_node = Node(neighbour1, color, copy.deepcopy(root.board))
                                        new_node.board.place(color, neighbour1)
                                        root.add_child(new_node)
                                        visited[neighbour1] = True
                                        possibles[i].append(new_node)
            else:
                for move in possibles[i - 1]:
                    visited = defaultdict(bool)
                    path = move.board.connected_coords(move.move)
                    if move.color == "red":
                        coords = [coord[0] for coord in path]
                        if min(coords) == 0 and max(coords) == self.board.n - 1:
                            if self.color == "red":
                                move.value = self.board.n ** 2
                            else:
                                move.value = -(self.board.n ** 2)
                            if i == 1:
                                return root
                            continue
                    else:
                        coords = [coord[1] for coord in path]
                        if min(coords) == 0 and max(coords) == self.board.n - 1:
                            if self.color == "blue":
                                move.value = self.board.n ** 2
                            else:
                                move.value = -(self.board.n ** 2)
                            if i == 1:
                                return root
                            continue
                    for j in range(root.board.n):
                        for k in range(root.board.n):
                            if root.board[(j, k)]:
                                for neighbour1 in root.board._coord_neighbours((j, k)):
                                    # for neighbour2 in move.board._coord_neighbours(neighbour1):
                                        neighbour1 = (int(neighbour1[0]), int(neighbour1[1]))
                                        if not visited[neighbour1] and not move.board[neighbour1]:
                                            if is_red:
                                                color = "red"
                                            else:
                                                color = "blue"
                                            new_node = Node(neighbour1, color, copy.deepcopy(move.board))
                                            new_node.board.place(color, neighbour1)
                                            move.add_child(new_node)
                                            visited[neighbour1] = True
                                            possibles[i].append(new_node)
            is_red = not is_red
        return root

    def minimax(self, node, alpha, beta, depth=0, is_max=True):
        def eval(node):
            red_eval = self.board.n ** 2
            blue_eval = self.board.n ** 2
            value = defaultdict(int)
            for i in range(node.board.n):
                for j in range(node.board.n):
                    if not value[(i, j)]:
                        if node.board[(i, j)] == "red":
                            red = bfs_red((i, j), node.board, value)
                            if red < red_eval:
                                red_eval = red
                        elif node.board[(i, j)] == "blue":
                            blue = bfs_blue((i, j), node.board, value)
                            if blue < blue_eval:
                                blue_eval = blue
            if self.color == "blue":
                return red_eval - blue_eval 
            else:
                return blue_eval - red_eval

        if not node.children:
            if not node.value:
                value = eval(node)
                node.value = value - depth
            return node.value

        if is_max:
            best_value = -math.inf
            for child in node.children:
                value = self.minimax(child, alpha, beta, depth + 1, False)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            node.value = best_value - depth
            return best_value - depth
        else:
            best_value = math.inf
            for child in node.children:
                value = self.minimax(child, alpha, beta, depth + 1, True)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            node.value = best_value - depth
            return best_value - depth
