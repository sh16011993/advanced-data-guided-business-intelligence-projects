import pandas as pd
import numpy as np
import sys
from igraph import *
from scipy import spatial

# This function computes the cosine similarity
def compute_cos_similarity(noVertices):
	cos_sim = [[0.0 for x in range(noVertices)] for y in range(noVertices)]
	for i in range(noVertices):
		vert_i = g.vs.select(i)[0].attributes().values()
		for j in range(i, noVertices) :
			vert_j = g.vs.select(j)[0].attributes().values()
			cos_sim[i][j] = 1.0 - spatial.distance.cosine(vert_i, vert_j)
			cos_sim[j][i] = 1.0 - spatial.distance.cosine(vert_i, vert_j)
	return(cos_sim)

# This function returns the community to which a particular node belongs
def find_community(communities, node):
	for community in communities.keys():
		if(node in communities[community]):
			return(community)

# This function computes the newman gain
def compute_newman_gain(community, node, edgescount):
	# Link strength of node from all the community members
	#print('Node: ', str(node))
	total = 0.0
	for member in community:
		if(g.are_connected(node, member)):
			total = total + g.es[g.get_eid(node, member)]["weight"]	
	#print('EdgesCount: ', str(edgescount))
	#print('Total: ', str(total))	
	#print('Node: ', str(node), ' has degree: ', str(g.degree(node)))
	return((1.0/float(2*edgescount))*(total - float(sum(g.degree(community)) * g.degree(node)) / float(2 * edgescount)))
	#return((1/(2*edgescount))*(total - sum(g.degree(community)) * g.degree(node) / (2 * edgescount)))

# This function computes the attribute gain
def compute_attr_gain(community, node, cos_sim, commlength):
	q_attr = 0.0
	for member in community:
		q_attr = q_attr + cos_sim[member][node]
	#return(q_attr)
	return(q_attr/float(len(community)*commlength))

# This function computes the modularity gain using the newman and attribute gain
def compute_composite_modularity_gain(community, node, noEdges, sim, commlength):
	q_nm = compute_newman_gain(community, node, noEdges)
	q_attr = compute_attr_gain(community, node, sim, commlength)
	return(alpha*q_nm + (1-alpha)*q_attr)

def part1():
	noVertices = g.vcount()
    noEdges = g.ecount()
	communities = dict()
	for node in range(noVertices):
		communities[node] = [node]
	# Finding the cos_sim
	sim = compute_cos_similarity(noVertices)
	flag = 1
	# Part 1 goes for 15 iterations or till convergence whichever earlier
	for counter in range(15):
		for node in range(noVertices):
			curr_community = find_community(communities, node)
			maxgain = 0
			maxcomm = -1
			for community in communities.keys():
				if(sorted(communities[community]) != sorted(communities[curr_community])):
					gain = compute_composite_modularity_gain(communities[community], node, noEdges, sim, len(communities))
					if(gain > 0 and gain > maxgain):
						maxgain = gain
						maxcomm = community
			if(maxgain > 0):
				#print(maxgain)
				communities[curr_community].remove(node)
				communities[maxcomm].append(node)
				flag = 0
				if(len(communities[curr_community]) == 0):
					del communities[curr_community]
		if(flag == 1):
			break
	return(communities)
	
# Reducing the size of the graph by grouping together the members of the community	
def communityToNode(communities):
	communityIndex = 0
	membership = list(range(0, g.vcount()))
	for community in communities.keys():
		for vertex in communities[community]:
			membership[vertex] = communityIndex
		communityIndex += 1
	g.contract_vertices(membership, combine_attrs=mean)
	g.simplify(combine_edges=min)

def part2(previousCommunities, communities, iteration):
	if(iteration == 0):
		communityIndex = 0
        for community in communities.keys():
			previousCommunities[communityIndex] = communities[community]
			communityIndex += 1
	else:
		newCommunities = dict()
		communityIndex = 0
		for community in communities.keys():
			temp = []
			for vertex in communities[community]:
				temp.extend(previousCommunities[vertex])
			newCommunities[communityIndex] = temp
			communityIndex += 1
		previousCommunities = newCommunities.copy()
	return(previousCommunities)

# Function to write the communities to a file
def writeCommunities(communities, alpha):
	if(alpha == 0.5):
		alpha = 5
	fileName = "communities_" + str(int(alpha)) + ".txt"
	with open(fileName, 'w') as f:
		for community in communities.keys():
			for vertex in sorted(communities[community]):
				f.write(str(vertex) + ", ")
			f.write("\n")
	
if len(sys.argv) != 2:
	print('Commandline argument mismatch. Please provide only one argument equal to the value of alpha')
else:
	# Getting alpha 
	alpha = float(sys.argv[1])
	
	# First getting all the input
	nodes = pd.read_csv('data/fb_caltech_small_attrlist.csv')
	
	with open('data/fb_caltech_small_edgelist.txt') as f:
		edges = f.readlines()
	edges = [tuple(int(x) for x in line.strip().split(" ")) for line in edges]
	# Input reading complete
	
	# Getting the number of nodes
	nodeCount = nodes.shape[0]
	
	# Forming Graph
	g = Graph()
	g.add_vertices(nodeCount)
	g.add_edges(edges)
	g.es['weight'] = [1 for e in range(len(edges))]
	for attr in nodes.columns.values:
		g.vs[attr] = list(nodes[attr])
	# Graph ready
	
	communities = dict()
    previousCommunities = dict()
	# Iterating part 1 and part 2 - 15 times
	tracker = 0
	while tracker < 15:
		if(tracker != 0):
			communityToNode(communities)
		communities = part1()
		if(len(communities) == len(previousCommunities)):
			break
        else:
			previousCommunities = part2(previousCommunities, communities, tracker)
			if(len(previousCommunities) < 17):
				break
		tracker = tracker + 1
	writeCommunities(previousCommunities, alpha)
