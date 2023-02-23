from collections import defaultdict
from referee.log import comment

def bfs_red(start, board, value):
    stack = [start]
    visited = defaultdict(bool)
    visited[start] = True
    prev = {}
    reached_up = reached_down = False
    path = []
    eval = 0
    connected = [start]

    while stack:
        node = stack.pop(0)
        if node[0] == board.n - 1 and not reached_up:
            reached_up = True
            stack = list(filter(lambda x: x[0] < board.n - 1, stack))
            cur = node
            while cur != start:
                if board[cur] != "red" and cur not in path:
                    eval += 1
                else:
                    path.append(cur)
                cur = prev[cur]
        elif node[0] == 0 and not reached_down:
            reached_down = True
            stack = list(filter(lambda x: x[0] > 0, stack))
            cur = node
            while cur != start:
                if board[cur] != "red" and cur not in path:
                    eval += 1
                else:
                    path.append(cur)
                cur = prev[cur]
        if reached_down and reached_up:
            for node in connected:
                value[node] = eval
            value[start] = eval
            return eval
        neighbours = board._coord_neighbours(node)
        if reached_down:
            neighbours = list(filter(lambda x: x[0] >= 0, neighbours))
        elif reached_up:
            neighbours = list(filter(lambda x: x[0] <= board.n, neighbours))
        for neighbour in neighbours:
            if board[neighbour] == "blue":
                continue
            
            if not visited[neighbour] and neighbour not in stack:
                prev[neighbour] = node
                if board[neighbour] == "red":
                    if node in connected:
                        connected.append(neighbour)
                    stack = [neighbour] + stack
                else:
                    stack.append(neighbour)
        visited[node] = True
    return board.n ** 2

def bfs_blue(start, board, value):
    stack = [start]
    visited = defaultdict(bool)
    visited[start] = True
    prev = {}
    reached_up = reached_down = False
    path = []
    eval = 0
    connected = [start]

    while stack:
        node = stack.pop(0)
        if node[1] == board.n - 1 and not reached_up:
            reached_up = True
            stack = list(filter(lambda x: x[1] < board.n - 1, stack))
            cur = node
            while cur != start:
                if board[cur] != "blue" and cur not in path:
                    eval += 1
                cur = prev[cur]
        elif node[1] == 0 and not reached_down:
            reached_down = True
            stack = list(filter(lambda x: x[1] > 0, stack))
            cur = node
            while cur != start:
                if board[cur] != "blue" and cur not in path:
                    eval += 1
                cur = prev[cur]
        if reached_down and reached_up:
            for node in connected:
                value[node] = eval
            return eval
        neighbours = board._coord_neighbours(node)
        if reached_down:
            neighbours = list(filter(lambda x: x[1] >= 0, neighbours))
        elif reached_up:
            neighbours = list(filter(lambda x: x[1] <= board.n, neighbours))
        for neighbour in neighbours:
            if board[neighbour] == "red":
                continue
            if not visited[neighbour] and neighbour not in stack:
                prev[neighbour] = node
                if board[neighbour] == "blue":
                    if node in connected:
                        connected.append(neighbour)
                    stack = [neighbour] + stack
                else:
                    stack.append(neighbour)
        visited[node] = True
    return board.n ** 2