# -*-coding: utf-8 -*-


def get_node_friends(new_g, origin_g, node):
    friends = origin_g.neighbors(node)

    for friend in friends:
        new_g.add_edge(node, friend)


def snowballSamplingEndByNodes(g, origin_g, center, target_nodes_set, current_nodes_set=set([]), taboo_set=set([])):
    #if center == 2001627641:
    #    print center, len(target_nodes_set), len(current_nodes_set), len(taboo_set)

    if len(current_nodes_set) == len(target_nodes_set):
        # 终止条件
        # print 'reach target nodes size'
        return taboo_set

    if center in taboo_set:
        # Visited this node -- exit
        return taboo_set
    else:
        # new node, don't visit again
        g.add_node(center)
        taboo_set.add(center)

    get_node_friends(g, origin_g, center)
    for node in g.neighbors(center):
        taboo_set = snowballSamplingEndByNodes(g, origin_g, node, target_nodes_set, current_nodes_set=set(g.nodes()), taboo_set=taboo_set)

    return taboo_set

def multi_snowballSamplingEndByNodes(g, origin_g, centers, target_nodes_set, taboo_set=set([])):
    taboo_set = set()    
    
    for centerid in centers:
        # print 'start snowball_sampling from %s' % centerid
        taboo_set = snowballSamplingEndByNodes(g, origin_g, centerid, target_nodes_set, current_nodes_set=set(g.nodes()), taboo_set=taboo_set)
    
    return taboo_set
