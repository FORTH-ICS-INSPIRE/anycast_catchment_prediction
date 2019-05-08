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
#from bgp_simulator_anycast_coloring import *
import copy
import numpy as np

LARGE_NUMBER = 100000

def evaluate_efficiency(current_node, GGG, list_of_Rgraph_colors, list_of_probabilities, lazy_probabilities_threshold, lazy_state_space_sampling):
	CC = defaultdict(dict)
	current_list_of_Rgraph_colors = []
	current_list_of_probabilities = []
	efficiency = 0
	if (lazy_state_space_sampling is None) or (lazy_state_space_sampling >= len(list_of_Rgraph_colors)):
		lazy_list_of_Rgraph_colors = list_of_Rgraph_colors
		lazy_list_of_probabilities = list_of_probabilities
	else:
		indices = np.random.choice(len(list_of_Rgraph_colors), size=lazy_state_space_sampling, replace=False, p=list_of_probabilities)
		lazy_list_of_Rgraph_colors = [list_of_Rgraph_colors[i] for i in indices]
		lazy_list_of_probabilities = [list_of_probabilities[i] for i in indices]
		normalization_factor = sum(lazy_list_of_probabilities)
		lazy_list_of_probabilities = [p/normalization_factor for p in lazy_list_of_probabilities]
	for i, current_R_colors in enumerate(lazy_list_of_Rgraph_colors):
		GGG.colors = copy.deepcopy(current_R_colors)#
		initial_nb_certain_nodes = GGG.get_nb_of_nodes(with_certain_color=True)
		if GGG.has_certain_color(current_node): # if has certain color for this routing configuration, skip the following loop
			current_list_of_Rgraph_colors.append( copy.deepcopy(GGG.colors) )#
			current_list_of_probabilities.append( lazy_list_of_probabilities[i])
			efficiency = efficiency + initial_nb_certain_nodes * lazy_list_of_probabilities[i] 
			continue
		current_color_dict = GGG.get_color(current_node)
		for color, prob in current_color_dict.items():
			if prob < lazy_probabilities_threshold:
				continue
			GGG.add_certain_color_to_node(current_node, color, update_color_of_neighbors=True)
			CC[color] = GGG.get_nb_of_nodes(with_certain_color=True) 
			current_list_of_Rgraph_colors.append( copy.deepcopy(GGG.colors) )#
			current_list_of_probabilities.append( prob * lazy_list_of_probabilities[i])
			GGG.colors = copy.deepcopy(current_R_colors)
			efficiency = efficiency + CC[color] * prob * lazy_list_of_probabilities[i]
	return (current_list_of_Rgraph_colors, current_list_of_probabilities, efficiency)



def greedy_next_node(GGG, candidate_nodes, list_of_selected_nodes, list_of_Rgraph_colors, list_of_probabilities, current_efficiency, previous_added_efficiencies, lazy_evaluations, lazy_probabilities_threshold, lazy_state_space_sampling):
	dict_current_list_of_Rgraph_colors = defaultdict(list)
	dict_current_list_of_probabilities = defaultdict(list)
	efficiency = defaultdict(lambda:0)
	j = 0
	while j < len(candidate_nodes):
		#print('Candidate nodes to check: {}'.format(len(candidate_nodes)-j), end='\r')
		current_node = candidate_nodes[j]
		j = j + 1
		(dict_current_list_of_Rgraph_colors[current_node], dict_current_list_of_probabilities[current_node], efficiency[current_node]) = \
															evaluate_efficiency(current_node, GGG, list_of_Rgraph_colors, list_of_probabilities, lazy_probabilities_threshold, lazy_state_space_sampling)
		if lazy_evaluations and (j < len(candidate_nodes)):
			if (efficiency[current_node] - current_efficiency) > previous_added_efficiencies[candidate_nodes[j]]:
				break
	best_node = sorted(efficiency, key=efficiency.get)[-1]	
	#print(' ')

	
	##print([efficiency[n]-current_efficiency for n in sorted(efficiency, key=efficiency.get, reverse=True) ])
	##print(efficiency[best_node]-current_efficiency)

	candidate_nodes.remove(best_node)
	list_of_selected_nodes.append(best_node)
	for i, current_R_colors in enumerate(dict_current_list_of_Rgraph_colors[best_node]):
		GGG.colors = copy.deepcopy(current_R_colors)#current_R_colors.copy()
		GGG.update_forward_probabilistic_coloring()
		dict_current_list_of_Rgraph_colors[best_node][i] = copy.deepcopy(GGG.colors)#GGG.colors.copy()
	list_of_Rgraph_colors = dict_current_list_of_Rgraph_colors[best_node]
	list_of_probabilities = dict_current_list_of_probabilities[best_node]
	for k, eff in efficiency.items():
		previous_added_efficiencies[k] = eff - current_efficiency
	del previous_added_efficiencies[best_node]
	current_efficiency = efficiency[best_node]
	candidate_nodes = sorted(previous_added_efficiencies, key=previous_added_efficiencies.get, reverse=True)

	return (candidate_nodes, list_of_selected_nodes, list_of_Rgraph_colors, list_of_probabilities, current_efficiency, previous_added_efficiencies)


def greedy_measurements(GGG, candidate_nodes, budget, lazy_evaluations=False, lazy_probabilities_threshold=0,lazy_state_space_sampling=None):
	list_of_selected_nodes = []
	list_of_Rgraph_colors = [GGG.colors]
	list_of_probabilities = [1]
	current_efficiency = GGG.get_nb_of_nodes(with_certain_color=True)
	list_of_efficiencies = []
	list_of_efficiencies.append(current_efficiency)
	previous_added_efficiencies = {k:LARGE_NUMBER for k in candidate_nodes}
	while len(list_of_selected_nodes) < budget:
		#t = tictoc()
		#print('Iteration: {}'.format(len(list_of_selected_nodes)))
		(candidate_nodes, list_of_selected_nodes, list_of_Rgraph_colors, list_of_probabilities, current_efficiency, previous_added_efficiencies) = \
				greedy_next_node(GGG, candidate_nodes, list_of_selected_nodes, list_of_Rgraph_colors, list_of_probabilities, current_efficiency, previous_added_efficiencies, lazy_evaluations, lazy_probabilities_threshold, lazy_state_space_sampling)
		list_of_efficiencies.append(current_efficiency)
		#print(list_of_selected_nodes)
		#print(list_of_efficiencies)
		##print(list_of_probabilities)
		#t = tictoc(t)
		#print(' ')

	return (list_of_selected_nodes, list_of_efficiencies)


def random_measurements(GGG, candidate_nodes, budget, lazy_probabilities_threshold=0, lazy_state_space_sampling=None):
	list_of_selected_nodes = random.sample(candidate_nodes,budget)
	list_of_Rgraph_colors = [GGG.colors]
	list_of_probabilities = [1]
	current_efficiency = GGG.get_nb_of_nodes(with_certain_color=True)
	list_of_efficiencies = []
	list_of_efficiencies.append(current_efficiency)
	#t = tictoc()
	i = 0
	for current_node in list_of_selected_nodes:
		i+=1
		#print('Iteration: {}'.format(i),end='\r')
		(list_of_Rgraph_colors, list_of_probabilities, current_efficiency) = evaluate_efficiency(current_node, GGG, list_of_Rgraph_colors, list_of_probabilities, lazy_probabilities_threshold, lazy_state_space_sampling)
		list_of_efficiencies.append(current_efficiency)
	#print(list_of_selected_nodes)
	#print(list_of_efficiencies)
	##print(list_of_probabilities)
	#print(' ')
	#t = tictoc(t)
	#print(' ')

	return (list_of_selected_nodes, list_of_efficiencies)