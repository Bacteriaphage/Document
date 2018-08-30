"""
little dependancy graph
"""

import logging


class Node:
    
    def __init__(self, value, valid, name):
        self.value = value
        self.valid = valid
        self.name = name
        
    def get(self):
        return self.value

    def set(self, v):
        self.value = v
    
    def invalidate(self):
        self.valid = False
    
    def validate(self):
        self.valid = True

        
class Dependancy:
    
    def __init__(self, data, relations):
        self.relations = relations
        self.graph = Dependancy.build_graph(self.relations)
        self.r_graph = Dependancy.build_r_graph(self.relations)
        self.topo = Dependancy.topo_sort(relations, self.r_graph, self.graph)
        self.nodes = Dependancy.create_node(self.topo)
        self.init_node(data, relations, self.topo)
        
    @classmethod
    def create_node(cls, topo):
        nodes = dict()
        for name in topo:
            nodes[name] = Node(None, False, name)
        return nodes
    
    def init_node(self, data, relations, topo):
        for name in topo:
            # if this is a literal node
            if relations[name]['args'] == None:
                self.nodes[name].set(relations[name]['func'](*data[name]))
                self.nodes[name].validate()
            else:
                self.nodes[name].set(relations[name]['func'](*[self.nodes[node_name].get() for node_name in relations[name]['args']]))
                self.nodes[name].validate()
            
    @classmethod
    def topo_sort(cls, relations, r_graph, graph):
        topo_array = list()
        in_degree = dict()
        roots = set()
        for key in relations.keys():
            in_degree[key] = 0
            roots.add(key)
        for key, value in r_graph.items():
            in_degree[key] = len(value)
            roots.remove(key)
        roots = list(roots)
        topo_array.extend(roots)
        while len(roots):
            if roots[0] not in graph:
                del roots[0]
                continue
            for next_node in graph[roots[0]]:
                in_degree[next_node] -= 1
                if in_degree[next_node] == 0:
                    del in_degree[next_node]
                    roots.append(next_node)
                    topo_array.append(next_node)
            del roots[0]
            
        if len(topo_array) != len(relations):
            raise RuntimeError('circle detected in graph!')
            
        return topo_array
    
    @classmethod
    def build_r_graph(cls, relations):
        graph = dict()
        for key, value in relations.items():
            if value['args'] == None:
                continue
            graph[key] = value['args']
        return graph
    
    @classmethod
    def build_graph(cls, relations):
        r_graph = dict()
        for key, value in relations.items():
            if value['args'] == None:
                continue
            for arg in value['args']:
                if arg in r_graph:
                    r_graph[arg].append(key)
                else:
                    r_graph[arg] = [key]
        return r_graph
        
    def evaluate(self, node):
        if node.name not in self.r_graph:
            return
        else:
            args = self.relations[node.name]['args']
            node.value = self.relations[node.name]['func'](*[self.getter(name) for name in args])
            node.valid = True
            
    def invalidate(self, node):
        if node.name in self.graph:
            for next_node_name in self.graph[node.name]:
                self.nodes[next_node_name].valid = False
                self.invalidate(self.nodes[next_node_name])
            
    def setter(self, node_name, data):
        logging.info('set first value to a new value')
        node = self.nodes[node_name]
        node.value = data
        if node.name in self.r_graph:
            raise RuntimeError("Cannot set new value to a non canset node {}".format(node.name))
        self.invalidate(node)
    
        
    def getter(self, node_name):
        node = self.nodes[node_name]
        if node.valid == True:
            return node.value
        else:
            self.evaluate(node)
            return node.value
        
    
# relations = {'name':{'func': function, 'args': args}, }
if __name__ == '__main__':
    
    if 0:
        # demo 1:
        #    ------>third
        #    |        ^
        #    |        | 
        # first---->second
        relations = {'first':{'func': lambda x: x, 'args': None},
                     'second':{'func': lambda x: 2 * x, 'args':['first']},
                     'third':{'func': lambda x, y: (x + 100) * y, 'args':['first', 'second']}
                    }
        data = {'first': [1]}
        DG = Dependancy(data, relations)
        logging.info((DG.getter('first'), DG.getter('second'), DG.getter('third')))
        DG.setter('first', 2)
        logging.info((DG.getter('first')))
        logging.info((DG.getter('first'), DG.getter('second'), DG.getter('third')))
    if 1:
        # demo 2:
        #    ------>third
        #    |        ^
        #    |        | 
        # first     second
        relations = {'first':{'func': lambda x: x, 'args': None},
                     'second':{'func': lambda x, y: x * y, 'args': None},
                     'third':{'func': lambda x, y: (x + 100) * y, 'args':['first', 'second']}
                    }
        data = {'first': [1], 'second':[2, 3]}
        DG = Dependancy(data, relations)
        logging.info((DG.getter('first'), DG.getter('second'), DG.getter('third')))
        DG.setter('first', 2)
        logging.info((DG.getter('first'), DG.getter('second'), DG.getter('third')))
        DG.setter('second', 2)
        logging.info((DG.getter('first'), DG.getter('second'), DG.getter('third')))
        
