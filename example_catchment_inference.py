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
from create_Rgraph_from_Topo import *
import time
import json
import random




### Define parameters ###
AS_relationship_dataset = './CAIDA AS-graph/20190401.as-rel2.txt' # an AS topology with the format provided by the CAIDA AS-relationships dataset http://www.caida.org/data/as-relationships/
nb_of_anycasters = 2 # an int number denoting the number of anycasters / ingress points
shortest_path_preference = True # boolean. I.e., to use (True) or not (False) Algorithm 5 from [1]
### end of parameter definition ###

print('Loading topology...')
Topo = BGPtopology()
Topo.load_topology_from_csv(AS_relationship_dataset)
list_of_ASNs = Topo.get_all_nodes_ASNs()

print('Simulating BGP...')
anycasters = random.sample(list_of_ASNs, nb_of_anycasters)
		
prefix = 0	# denote the prefix that will be anycaster by the anycasters, e.g., denote a prefix arbitrarity (here, the prefix is denoted with an int, i.e., zero "0")
for AS in anycasters:
	Topo.add_prefix(AS, prefix)

	
print('Creating Rgraph...')
G = create_Rgraph_from_Topo(Topo, prefix, shortest_path_preference=shortest_path_preference) # i.e., Algorithm 1 from [1]

print('Probabilistic coloring...')
G.set_probabilistic_coloring(anycasters)  # i.e., Algorithms 2 and 3 from [1]

print('Clearing routing information...')
Topo.clear_routing_information()

# get results
CC = G.get_certain_catchment()
PC = G.get_probabilistic_catchment()
