# python3
#
# Author: Pavlos Sermpezis
# Institute of Computer Science, Foundation for Research and Technology - Hellas (FORTH), Greece
#
# E-mail: sermpezis@ics.forth.gr
#
#
# example for catchment inference, see related paper:
# 	[1] Pavlos Sermpezis and Vasileios Kotronis. “Inferring Catchment in Internet Routing”, ACM SIGMETRICS, 2019.
#


from BGPtopology import BGPtopology
from Rgraph import *


'''
Creates the R-graph for the given Topology and prefix. 
CURRENT VERSION: assumes that anycasting takes place (i.e., more than nodes announce the given prefix)

(i) starts the Rgraph by adding the anycasting nodes, 
then iterates over all nodes, and for each node:
(ii) adds an incoming edge from its neighbors from which it received the best path to the given prefix
(iii) adds incoming edges from all its neighbors from which it learned a path to the given prefix (not the best path) IF the neighor is of equal type/preference as the best path neighbor...
(iii.a) ... and [IF shortest_path_preference==True] and has the same length as the best path

Input argument:
	(a) Topo: an AS topology object
	(b) prefix: the prefix for which the Rgraph will be constructed
	(c) shortest_path_preference: True/False for not adding in the Rgraph edges for paths that are longer than the best path

Output:
	The Rgraph
'''
def create_Rgraph_from_Topo(Topo, prefix, shortest_path_preference=False):

	# create an empty Rgraph
	G = Rgraph()	

	# find all nodes that announce the prefix, and add them in the set "anycaster_ASes", and add them as nodes in the Rgraph
	anycaster_ASes = set()
	for ASN in Topo.get_all_nodes_ASNs():
		if Topo.get_node(ASN).has_prefix(prefix):	# if the node is announcing the prefix
			anycaster_ASes.add(ASN)	
			G.add_node(ASN)
	assert len(anycaster_ASes)>1, "Number of Anycasters <= 1"

	# iterate over all nodes and ...
	for ASN in Topo.get_set_of_nodes_with_path_to_prefix(prefix):
		if ASN in anycaster_ASes:
			continue

		# ... find best path, and add link in the Rgraph to this neighbor
		best_path = Topo.get_node(ASN).get_path(prefix)	# the best path of ASN to the prefix (i.e., a list of type [neighborAS1 AS2 AS3.... originAS])
		best_path_neighbor_ASN = best_path[0] # the neighbor through which this best path is received
		best_path_neighbor_type = Topo.get_node(ASN).ASneighbors[best_path_neighbor_ASN] # the type (1 for provider, 0 for peer, -1 for customer) of this neighbor 
		G.add_edge(best_path_neighbor_ASN,ASN,Topo.get_node(ASN).ASneighbors_preference[best_path_neighbor_ASN]) # add in the Rgraph a directed edge from the "best_path_neighbor_ASN" to "ASN

		# ... find othar paths, and add link in the Rgraph to these neighbors, if the necessary conditions (equal type & path length) are satisfied
		all_paths = Topo.get_node(ASN).all_paths[prefix]	# a dictionary with all received paths for the prefix (keys: the ASN of the neighbor that sent the path, values: the corresponding AS path)
		for neighbor_ASN in all_paths.keys():
			neighbor_type = Topo.get_node(ASN).ASneighbors[neighbor_ASN] 
			if neighbor_type == best_path_neighbor_type: # if this neighbor is of the same type/preference with the neighbor of the best path, add an edge in the Rgraph
				if (not shortest_path_preference) or ( len(all_paths[neighbor_ASN])==len(best_path) ): # check also "shortest_path_preference" option (if False: first condition is satisfied always, if True: it needs second condition to be satisfied, i.e., the path of equal length to the best path)
					G.add_edge(neighbor_ASN,ASN)

	return G
