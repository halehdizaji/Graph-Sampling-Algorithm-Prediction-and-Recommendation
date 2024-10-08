import random
import networkx as nx
import networkit as nk
from typing import Union
import sys
sys.path.append('../../')
from littleballoffur.sampler import Sampler


NKGraph = type(nk.graph.Graph())
NXGraph = nx.classes.graph.Graph


class MetropolisHastingsRandomWalkSampler(Sampler):
    r"""An implementation of node sampling by Metropolis Hastings random walks.
    The random walker has a probabilistic acceptance condition for adding new nodes
    to the sampled node set. This constraint can be parametrized by the rejection
    constraint exponent. The sampled graph is always connected.  `"For details about the algorithm see this paper." <http://mlcb.is.tuebingen.mpg.de/Veroeffentlichungen/papers/HueBorKriGha08.pdf>`_

    Args:
        number_of_nodes (int): Number of nodes. Default is 100.
        seed (int): Random seed. Default is 42.
        alpha (float): Rejection constraint exponent. Default is 1.0.
    """

    def __init__(self, number_of_nodes: int = 100, seed: int = 42, alpha: float = 1.0):
        self.number_of_nodes = number_of_nodes
        self.seed = seed
        self.alpha = alpha
        self._set_seed()

    def _create_initial_node_set(self, graph, start_node):
        """
        Choosing an initial node.
        """
        if start_node is not None:
            if start_node >= 0 and start_node < self.backend.get_number_of_nodes(graph):
                self._current_node = start_node
                self._sampled_nodes = set([self._current_node])
            else:
                raise ValueError("Starting node index is out of range.")
        else:
            self._current_node = random.choice(
                range(self.backend.get_number_of_nodes(graph))
            )
            self._sampled_nodes = set([self._current_node])

    def _do_a_step(self, graph):
        """
        Doing a single random walk step.
        """
        score = random.uniform(0, 1)
        if len(list(nx.neighbors(graph, self._current_node))) == 0:
            print('no neighbors')
            return
        new_node = self.backend.get_random_neighbor(graph, self._current_node)
        ratio = float(self.backend.get_degree(graph, self._current_node)) / float(
            self.backend.get_degree(graph, new_node)
        )
        ratio = ratio ** self.alpha
        if score < ratio:
            self._current_node = new_node
            self._sampled_nodes.add(self._current_node)

    def sample(
        self, graph: Union[NXGraph, NKGraph], max_stucking_iter = 50, start_node: int = None
    ) -> Union[NXGraph, NKGraph]:
        """
        Sampling nodes with a Metropolis Hastings single random walk.

        Arg types:
            * **graph** *(NetworkX or NetworKit graph)* - The graph to be sampled from.
            * **start_node** *(int, optional)* - The start node.

        Return types:
            * **new_graph** *(NetworkX or NetworKit graph)* - The graph of sampled edges.
        """
        self._deploy_backend(graph)
        self._check_number_of_nodes(graph)
        self._create_initial_node_set(graph, start_node)
        stucking_iter = 0
        while len(self._sampled_nodes) < self.number_of_nodes:
            prev_sample_node_nums = len(self._sampled_nodes)
            print('starting a step')
            self._do_a_step(graph)
            new_sample_node_nums = len(self._sampled_nodes)
            if prev_sample_node_nums == new_sample_node_nums:
                print('no new sample')
                stucking_iter += 1
                if stucking_iter == max_stucking_iter:
                    break
            else:
                stucking_iter = 0

        new_graph = self.backend.get_subgraph(graph, self._sampled_nodes)
        return new_graph

if __name__=='__main__':
    node_nums = 1000
    #graph1 = nx.barabasi_albert_graph(node_nums, 3)
    graph1 = nx.erdos_renyi_graph(node_nums, 0.003)
    sampling_percent = 0.3
    max_stucking_iter = 50
    sample_node_nums = int(node_nums * sampling_percent)
    rj = MetropolisHastingsRandomWalkSampler(number_of_nodes=sample_node_nums)
    sample_graph = rj.sample(graph1, max_stucking_iter=max_stucking_iter)
    print('sample graph nodes ' + str(sample_graph.nodes))
    print('num sampled nodes ', len(sample_graph.nodes))
    print('sample graph edges: ' + str(sample_graph.edges))
    # print(sample1.edges())
    print(nx.degree(graph1))
