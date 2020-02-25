from numpy import *
import networkx as nx
import matplotlib.pyplot as plt



def get_root(direction):
    return globals(roots[direction])

class Root(object):
    def __init__(self, type_root=0, cost=1, direction1=(0, 0), direction2=(0, 0)):
        self.type_root = type_root
        self.direction1 = direction1
        self.direction2 = direction2
        self.cost = cost
        if cost == 1:
            self.distance(self)

    def distance(self):
        self.cost += 1
        if self.direction1 == start_points or self.direction1 == (0, 0):
            return
        else:
            if get_root(self.direction1).type_root == self.type_root:
                self.distance(get_root(self.direction1))
        if self.direction2 == start_points or self.direction2 == (0, 0):
            return
        else:
            if get_root(self.direction2).type_root == self.type_root:
                self.distance(get_root(self.direction2))


class Cell(object):
    def __init__(self, type_cell=0):
        # 0-gress 1-ground 2-stone Root-root :)
        self.type_cell = type_cell

def update_graph(graph=nx.MultiDiGraph()):
    cell = graph.nodes[0].__getattribute__("Cell")
    print(cell.type_cell)
    # for i in range(1,len(graph.nodes)):
    #     cell_t = graph[i]["Cell"]
    #     if cell_t.type_cell==0 or cell_t.type_cell==2:
    #         print(cell_t)


start_points = [(4, 5), (4, 6), (4, 7), (4, 8), (5, 4), (6, 4), (7, 4), (8, 4), (9, 5), (9, 6), (9, 7), (9, 8), (4, 9),
                (5, 9), (6, 9), (7, 9), (8, 9)]
game_field = nx.MultiDiGraph()

for i in range(1, 13):
    for j in range(1, 13):
        if (4 < i < 9) and (4 < j < 9):
            continue

        if i - 1 > 0:
            game_field.add_edge(str(i - 1) + str(j), str(i) + str(j))
            game_field.add_edge(str(i) + str(j), str(i - 1) + str(j))
        if j - 1 > 0:
            game_field.add_edge(str(i) + str(j - 1), str(i) + str(j))
            game_field.add_edge(str(i) + str(j), str(i) + str(j - 1))

        if i + 1 < 12:
            game_field.add_edge(str(i) + str(j), str(i + 1) + str(j))
            game_field.add_edge(str(i + 1) + str(j), str(i) + str(j))

        if j + 1 < 12:
            game_field.add_edge(str(i) + str(j), str(i) + str(j + 1))
            game_field.add_edge(str(i) + str(j + 1), str(i) + str(j))
        nx.set_node_attributes(game_field, Cell(), "Cell")
update_graph(game_field)
