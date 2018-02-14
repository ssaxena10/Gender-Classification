"""
cluster.py
"""
import networkx as nx
import matplotlib.pyplot as plt
import pickle


def partition_girvan_newman(graph):

    G = graph.copy()

    if G.order() == 1:
        return [G.nodes()]

    btw = nx.edge_betweenness_centrality(G)
    elist = sorted(btw.items(), key=lambda x: (-x[1]))
    csub = [c for c in nx.connected_component_subgraphs(G)]

    c = 0
    while len(csub) <= 4:
        edge_remove = elist[c]
        G.remove_edge(edge_remove[0][0], edge_remove[0][1])
        csub = [c for c in nx.connected_component_subgraphs(G)]

        c += 1

    return csub
    pass


def get_subgraph(graph, min):

    subnode = []
    for n in graph.nodes():
        if graph.degree(n) >= min:
            subnode.append(n)
    sgraph = graph.subgraph(subnode)
    return sgraph

    pass


def draw_network(graph, filename):

    plt.figure(figsize=(12, 12))
    getlabel = {n: '' if isinstance(n, int) else n for n in graph.nodes()}
    nx.draw_networkx(graph, labels=getlabel, alpha=.5, width=.1,
                     node_size=100)

    plt.axis("off")
    plt.savefig(filename)

    pass


def main():
    graph = nx.read_gpickle("graph.gpickle")
    print('graph has %d nodes and %d edges' % (graph.order(), graph.number_of_edges()))
    tot = 0
    pgn = partition_girvan_newman(graph)
    for i in pgn:
        tot += i.order()
    print('Partition: cluster 1 has %d nodes and cluster 2 has %d nodes' %
          (pgn[0].order(), pgn[1].order()))
    draw_network(pgn[0], "cluster0.png")
    draw_network(pgn[1], "cluster1.png")
    with open('output.pkl', 'rb') as f:
        output = pickle.load(f)
    output['community'] = 2
    output['avg'] = tot / output['community']
    pickle.dump(output, open('output.pkl', 'wb'))
    print("Community Detection, graph saved in cluster0.png,cluster1.png")


if __name__ == '__main__':
    main()
