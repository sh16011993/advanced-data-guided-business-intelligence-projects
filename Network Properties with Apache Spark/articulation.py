import sys
import time
import pandas as pd
import networkx as nx
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import functions
from graphframes import *
from copy import deepcopy

sc=SparkContext("local", "degree.py")
sqlContext = SQLContext(sc)

def articulations(g, usegraphframe=False):
    # Get the starting count of connected components
    # YOUR CODE HERE
    connectedComponents = g.connectedComponents().select("component").rdd.distinct().count()
    # Default version sparkifies the connected components process 
    # and serializes node iteration.
    if usegraphframe:
        l = list()
        # Get vertex list for serial iteration
	# YOUR CODE HERE
        vertices = g.vertices.map(lambda x: x.id).collect()
        for vertex in vertices:
            new_vertices = g.vertices.filter('id != "' + vertex + '"')
            new_edges = g.edges.filter('src != "' + vertex + '"').filter('dst != "' + vertex + '"')
	    # For each vertex, generate a new graphframe missing that vertex
	    # and calculate connected component count. Then append count to
	    # the output
	    # YOUR CODE HERE
            new_count = GraphFrame(new_vertices, new_edges).connectedComponents().select('component').distinct().count()
            if(new_count > connectedComponents):
                l.append((vertex, 1))
            else:
                l.append((vertex, 0))
        df = sqlContext.createDataFrame(sc.parallelize(l), ["id", "articulation"])
            	
    # Non-default version sparkifies node iteration and uses networkx 
    # for connected components count.
    else:
        # YOUR CODE HERE
        edges = g.edges
        src = edges.rdd.map(lambda x: (x[0]))
        dst = edges.rdd.map(lambda x: (x[1]))
        edges = pd.DataFrame({'source': src.collect(), 'target': dst.collect()}) 
        G = nx.from_pandas_edgelist(edges)
        a_points = set(nx.articulation_points(G))
        all_points = g.vertices.rdd.map(lambda x: (x.id, 1) if x.id in a_points else (x.id,0))
        df = sqlContext.createDataFrame(all_points, ["id", "articulation"])
    return df
		

filename = sys.argv[1]
lines = sc.textFile(filename)

pairs = lines.map(lambda s: s.split(","))
e = sqlContext.createDataFrame(pairs,['src','dst'])
e = e.unionAll(e.selectExpr('src as dst','dst as src')).distinct() # Ensure undirectedness 	

# Extract all endpoints from input file and make a single column frame.
v = e.selectExpr('src as id').unionAll(e.selectExpr('dst as id')).distinct()	

# Create graphframe from the vertices and edges.
g = GraphFrame(v,e)

#Runtime approximately 5 minutes
print("---------------------------")
print("Processing graph using Spark iteration over nodes and serial (networkx) connectedness calculations")
init = time.time()
df = articulations(g, False)
print("Execution time: %s seconds" % (time.time() - init))
print("Articulation points:")
df.filter('articulation = 1').show(truncate=False)
print("---------------------------")
#df.filter('articulation = 1').toPandas().to_csv("articulations_out.csv")

#Runtime for below is more than 2 hours
print("Processing graph using serial iteration over nodes and GraphFrame connectedness calculations")
init = time.time()
df = articulations(g, True)
print("Execution time: %s seconds" % (time.time() - init))
print("Articulation points:")
df.filter('articulation = 1').show(truncate=False)
