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


from collections import defaultdict, Counter
import networkx as nx 	# NOTE tested with networkx 2.1 (with versions 1.x it may not work)

class GraphNode:
	def __init__(self,ID):
		self.ID = ID
		self.route = None
		self.color = None
		self.is_colored_by_measurement = False


'''
Rgraph is a graph of type nx.DiGraph (directed graph), with:
	(a) nodes, with attributes 
			"color": dictionary with keys the root nodes of the graph, and values the probability the node to route towards the respective root node (or, "to have the color of the root node"); this information is either calculated from the Rgraph structure, or given as an oracle (from an external source to the Rgraph, e.g., from a simulation Topo).
					 [default value: None]
			"route": the route the node has selected (i.e., the best path); this information is given as an oracle (from an external source to the Rgraph, e.g., from a simulation Topo).
					 [default value: None]
	(b) directed edges, with attribute:
			"local_preference": if the directed edge is (I-->J), then this attribute is the local preference of node I for its neighbor J.
'''
class Rgraph():
	def __init__(self):
		#self.dict_of_nodes = defaultdict()
		self.nxG = nx.DiGraph()
		self.set_of_node_IDs_with_route_valid = set()
		self.routes_from_Topo = defaultdict()
		self.paths_from_Topo = defaultdict(list)
		self.routes_from_Graph = defaultdict()
		self.colors = defaultdict(dict)


	def print_info(self):
		print(nx.info(self.nxG))


	def has_node(self,ID):
		return self.nxG.has_node(ID)


	def has_edge(self,ID1,ID2):
		return self.nxG.has_edge(ID1,ID2)


	def add_node(self,ID):
		if not self.has_node(ID):
			self.nxG.add_node(ID, color=None, route=None)


	def add_edge(self,ID1,ID2, local_preference=None):	# directed edge ID1-->ID2, local_preference is the local preference of node ID2 to node ID1
		if not self.has_node(ID1):
			self.add_node(ID1)
		if not self.has_node(ID2):
			self.add_node(ID2)
		if not self.has_edge(ID1,ID2):
			self.nxG.add_edge(ID1,ID2,local_preference=local_preference)


	def remove_node(self,ID):
		self.nxG.remove_node(ID)


	def remove_edge(self,ID1,ID2):	
		self.nxG.remove_edge(ID1,ID2)


	def has_color(self,ID):
		#if self.nxG.nodes[ID]['color'] is None:
		if len(self.colors[ID]) == 0:
			return False
		else:
			return True

	def get_color(self,ID):
		if self.has_color(ID):
			#return self.nxG.nodes[ID]['color']
			return self.colors[ID]
		else:
			raise Exception('Node does not have color.')

	def remove_all_leaves(self):
		topo_sort = nx.topological_sort(self.nxG)
		for n in reversed(list(topo_sort)):
			if (len(list(self.nxG.successors(n))) == 0) and (len(list(self.nxG.predecessors(n))) == 1):
				self.remove_node(n)


	'''
	A color dictionary is "valid" when its values (that denote probabilities) sum to 1.0.
	'''
	def is_valid_color(self,color):
		epsilon = 0.0001 # to avoid accuracy errors due to rounding
		if (color is None) or ( abs(sum(color.values())-1.0) > epsilon ):
			return False
		else:
			return True

	'''
	"certain color" is defined when a node routes to a root node (or, takes color of the root node) with probability 1.0 (and takes all other colors with probability 0.0).
	'''
	def has_certain_color(self,ID):
		if self.has_color(ID) and ( max(self.get_color(ID).values())==1 ):
			return True
		else:
			return False


	def get_certain_color(self,ID):
		if self.has_certain_color(ID):
			for k,v in self.get_color(ID).items():
				if v==1:
					return k
		raise Exception('Node does not have certain color.')


	def has_route(self,ID):
		if self.nxG.nodes[ID]['route'] is None:
			return False
		else:
			return True


	def get_route(self,ID):
		if self.has_route(ID):
			return self.nxG.nodes[ID]['route']
		else:
			raise Exception('Node does not have route.')

	'''
	checks if the given "route" corresponds to a node in the Graph 
	'''
	def is_valid_route(self,route):
		if route in self.nxG.nodes():
			return True
		else:
			return False



	def get_list_of_nodes(self, with_color=False, with_certain_color=False, with_route=False, subset_of_nodes=None):
		conditions = [with_color, with_certain_color, with_route]
		nb_active_conditions = sum([1 for c in conditions if c])

		if subset_of_nodes is None:
			list_of_nodes = self.nxG.nodes()
		else:
			list_of_nodes = [n for n in self.nxG.nodes() if n in subset_of_nodes]

		if nb_active_conditions == 0:
			return list_of_nodes
		elif nb_active_conditions == 1:
			if with_color:
				return [n for n in list_of_nodes if self.has_color(n)]
			if with_certain_color:
				return [n for n in list_of_nodes if self.has_certain_color(n)]
			if with_route:
				return [n for n in list_of_nodes if self.has_route(n)]
		else:
			raise Exception('Cannot receive more than one active conditions.')


	def get_nb_of_nodes(self, with_color=False, with_certain_color=False, with_route=False, subset_of_nodes=None):
		return len(self.get_list_of_nodes(with_color=with_color, with_certain_color=with_certain_color, with_route=with_route, subset_of_nodes=subset_of_nodes))


	def set_route(self,ID,route):
		if self.has_route(ID):
			raise Exception('Node has already route.')
		if self.is_valid_route(route):
			raise Exception('The route is invalid.')	
		self.nxG.nodes[ID]['route'] = route



	'''
	### COLORING FUNCTIONS ###
	'''

	def color_node(self, ID, color_dict=None):
		if self.has_color(ID):
			raise Exception('Node has already color.')
		self.set_color(ID,color_dict=color_dict)

	'''
	colors node either it already as a color or not
	'''
	def recolor_node(self, ID, color_dict=None):
		#if not self.has_color(ID):
		#	raise Exception('Node (to be recolored) does not have color.')
		self.set_color(ID,color_dict=color_dict,recolor=True)


	'''
	Sets the color of a node
		(a) to the given color (if the color input argument is given)
		(b) from the colors of its predecessors in the Rgraph
	'''
	def set_color(self,ID,color_dict=None,recolor=False):
		if color_dict is not None:
			if not self.is_valid_color(color_dict):
				raise Exception('The color dictionary is invalid.')
			#self.nxG.nodes[ID]['color'] = color_dict
			self.colors[ID] = color_dict
		else:
			self.color_node_from_neighbors(ID,recolor=recolor)


	'''
	Calculates the color of a node from its predecessors, as follows: for each color...
		(i) sums the probabilities of the predecessors corresponding to this color
		(ii) normalizes the resulting value by diving it to the number of predecessors
	'''
	def color_node_from_neighbors(self,ID, recolor=False):
		set_of_predecessors = list(self.nxG.predecessors(ID))

		if len(set_of_predecessors) ==0:
			#print('WARNING: node does not have any predecessors.')
			return

		# create a color dict and values from color dicts of all predecessors
		color_dict = defaultdict()
		try:
			for p_ID in set_of_predecessors:
				color_dict = dict( Counter(color_dict) + Counter(self.get_color(p_ID)) ) # the method "get_color" raises an exception if the given node does not have a color
		except: 
			raise Exception('Not all predecessors are colored.')

		# normalize to [0,1] (i.e., dividing by the number of predecessors)
		for k,v in color_dict.items():
			color_dict[k] = 1.0*v/len(set_of_predecessors)

		if not self.is_valid_color(color_dict):
			raise Exception('Color from predecessors is not valid (sum of probabilities = {}).'.format(sum(color_dict.values())))

		# set the color of the node
		if recolor:
			self.recolor_node(ID, color_dict)
		else:
			self.color_node(ID, color_dict)


	'''
	Oracle-enhanced algorithm (for one node at each time): Adds the given color as the certain color to node, and updates certain colors to its neighbors if needed. 
		IF the node has already a certain color AND this is the same with the given color, THEN does nothing and returns
		IF the node has already a certain color BUT this is different than the given color, THEN it raises an exception
		IF the node does NOT already have a certain color, THEN:
			Sets this color as the certain color of the node.
			Checks if any of its neighbors (predecessors and successors) need to update its color to a certain color. IF yes, runs the same method (nested call of the function) for this neighbor.

	'''
	def add_certain_color_to_node(self, ID, certain_color, update_color_of_neighbors=True):
		if self.has_certain_color(ID):
			# for debugging purposes
			if self.get_certain_color(ID) != certain_color:
				raise Exception('Node already has certain color, different than the given one.')
			else:
				return
			#pass
			#print('Node has already certain color.')
	
		color_dict = {}
		color_dict[certain_color] = 1.0
		if not self.is_valid_color(color_dict):
			raise Exception("The given color {} is not valid".format(color_dict))
		self.set_color(ID,color_dict)

		if update_color_of_neighbors:
			# update colors of predecessors
			list_of_possible_predecessors = []
			for p_ID in self.nxG.predecessors(ID):
				if self.get_color(p_ID).get(certain_color,0) > 0:
					list_of_possible_predecessors.append(p_ID)
			if len(list_of_possible_predecessors) == 0:
				#  for debugging purposes
				raise Exception('This should not have happened: None of the predecessors of {} have its color {}'.format(ID, self.get_color(ID)))
			elif len(list_of_possible_predecessors) == 1:
				p_ID_to_color = list_of_possible_predecessors[0]
				if not self.has_certain_color(p_ID_to_color):
					self.add_certain_color_to_node(p_ID_to_color, certain_color, update_color_of_neighbors=True)

			# update colors of successors
			for s_ID in self.nxG.successors(ID):
				if not self.has_certain_color(s_ID):
					self.color_node_from_neighbors(s_ID, recolor=True)
					if self.has_certain_color(s_ID):
						if self.get_certain_color(s_ID) != certain_color:
							raise Exception('Successor {} ({}) is colored with a different color than {} ({})'.format(s_ID, self.get_color(s_ID), ID, self.get_color(ID) ))
						self.add_certain_color_to_node(s_ID, certain_color, update_color_of_neighbors=True)




	'''
	Updates the probabilistic coloring of the Rgraph.
		(i) calculates a topological sorting of the nodes (https://en.wikipedia.org/wiki/Topological_sorting)
		(ii) iterating over the nodes in the topological sorting that DO NOT have certain color, colors them based on their predecessors
	'''
	def update_forward_probabilistic_coloring(self):
		nodes_to_skip = self.get_list_of_nodes(with_certain_color=True)
		topo_sort = nx.topological_sort(self.nxG)
		for ID in topo_sort:
			if ID in nodes_to_skip:
				continue
			else:
				self.recolor_node(ID) # no color_dict as input argument in color_node ==> color node from predecessors

	'''
	Sets the probabilistic coloring of the Rgraph.
		(i) assigns to each source/root node the color of itself (i.e., source node I has as color {I:1.0})
		(ii) calculates a topological sorting of the nodes (https://en.wikipedia.org/wiki/Topological_sorting)
		(iii) iterating over the nodes in the topological sorting, colors them based on their predecessors
	'''
	def set_probabilistic_coloring(self, source_nodes):
		# color the source nodes (i.e., the roots of the Rgraph)
		for ID in source_nodes:
			if not self.has_node(ID):
				raise Exception("The source node {} is not in the graph".format(ID))
			if len(list(self.nxG.predecessors(ID))) >0:
				raise Exception("The source node {} is not a root".format(ID))
			if self.has_color(ID):
				raise Exception("The source node {} already has a color".format(ID))
			color_dict = dict.fromkeys(source_nodes,0)
			color_dict[ID] = 1.0
			self.color_node(ID,color_dict)

		# color the other nodes (non roots), based on the color of their neighbors
		topo_sort = nx.topological_sort(self.nxG)
		for ID in topo_sort:
			if ID in source_nodes:
				continue
			else:
				self.color_node(ID) # no color_dict as input argument in color_node ==> color node from predecessors

	'''
	Get the certain catchment for each anycaster (i.e., the number of nodes with the certain color of the anycaster).
	Returns a dictionary with keys: anycaster and values: certain catchment
	'''
	def get_certain_catchment(self, in_percentage=False, subset_of_nodes=None):
		dict_anycast_catchment = defaultdict(lambda:0)
		for ID in self.get_list_of_nodes(with_certain_color=True, subset_of_nodes=subset_of_nodes):
			dict_anycast_catchment[ self.get_certain_color(ID) ] += 1
		if in_percentage:
			total_nodes = self.get_nb_of_nodes()
			for k, v in dict_anycast_catchment.items():
				dict_anycast_catchment[k] = 1.0 * v / total_nodes
		return dict_anycast_catchment

	'''
	Get the probabilistic catchment for each anycaster (i.e., the sum of probabilities of nodes for the color of the anycaster).
	Returns a dictionary with keys: anycaster and values: probabilistic catchment
	'''
	def get_probabilistic_catchment(self, in_percentage=False, subset_of_nodes=None):
		dict_anycast_catchment = defaultdict(lambda:0)
		for ID in self.get_list_of_nodes(with_color=True, subset_of_nodes=subset_of_nodes):
			color_dict = self.get_color(ID)
			for anycaster, probability in color_dict.items():
				dict_anycast_catchment[ anycaster ] += probability
		if in_percentage:
			total_nodes = self.get_nb_of_nodes()
			for k, v in dict_anycast_catchment.items():
				dict_anycast_catchment[k] = 1.0 * v / total_nodes
		return dict_anycast_catchment


