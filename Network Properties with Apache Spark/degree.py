import sys
import pandas
import powerlaw
import networkx as nx
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from graphframes import *

sc=SparkContext("local", "degree.py")
sqlContext = SQLContext(sc)

''' return the simple closure of the graph as a graphframe.'''
def simple(g):
    # Extract edges and make a data frame of "flipped" edges
    # YOUR CODE HERE
    flipped = g.edges.map(lambda x: (x[1], x[0]))
    # Combine old and new edges. Distinctify to eliminate multi-edges
    # Filter to eliminate self-loops.
    # A multigraph with loops will be closured to a simple graph
    # If we try to undirect an undirected graph, no harm done
    # YOUR CODE HERE
    edges = g.edges.rdd.union(flipped.subtract(g.edges.rdd))
    edges = edges.filter(lambda x: (x[0] != x[1]))
    schemaString = "src dst"
    fields = [StructField(field_name, StringType(), True) for field_name in schemaString.split()]
    schema = StructType(fields)
    g = GraphFrame(g.vertices, sqlContext.createDataFrame(edges, schema))
    return(g)

''' Return a data frame of the degree distribution of each edge in the provided graphframe '''
def degreedist(g):
    # Generate a DF with degree,count
    # YOUR CODE HERE
    schemaString = "degree count"
    fields = [StructField(field_name, StringType(), True) for field_name in schemaString.split()]
    schema = StructType(fields)
    vertexDegree = sqlContext.createDataFrame(g.outDegrees.map(lambda y: (y[1], 1)).groupByKey().mapValues(sum), schema)
    return(vertexDegree)

''' Read in an edgelist file with lines of the format id1<delim>id2 and return a corresponding graphframe. If "large" we assume a header row and that delim = " ", otherwise no header and delim = ","'''
def readFile(filename, large, sqlContext=sqlContext):
    lines = sc.textFile(filename)
 
    if large:
        delim=" "
        # Strip off header row.
	lines = lines.mapPartitionsWithIndex(lambda ind,it: iter(list(it)[1:]) if ind==0 else it)
    else:
        delim=","

    # Extract pairs from input file and convert to data frame matching
    # schema for graphframe edges.
    # YOUR CODE HERE
    splitLines = lines.map(lambda l: l.split(delim))
    schemaString = "src dst"
    fields = [StructField(field_name, StringType(), True) for field_name in schemaString.split()]
    schema = StructType(fields)
    edges = sqlContext.createDataFrame(splitLines, schema)

    # Extract all endpoints from input file (hence flatmap) and create
    # data frame containing all those node names in schema matching
    # graphframe vertices
    # YOUR CODE HERE
    wordslist = lines.flatMap(lambda l: l.split(delim)).distinct().map(lambda y: [y])
    schemaString = "id"
    fields = [StructField(field_name, StringType(), True) for field_name in schemaString.split()]
    schema = StructType(fields)
    vertices = sqlContext.createDataFrame(wordslist, schema)
 
    # Create graphframe g from the vertices and edges.
    g = GraphFrame(vertices, edges)       

    return g

# main stuff

# If you got a file, yo, I'll parse it.
if len(sys.argv) > 1:
    filename = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2]=='large':
        large=True
    else:
        large=False

    print("Processing input file " + filename)
    g = readFile(filename, large)

    print("Original graph has " + str(g.edges.count()) + " directed edges and " + str(g.vertices.count()) + " vertices.")
    
    g2 = simple(g)
    print("Simple graph has " + str(g2.edges.count()/2) + " undirected edges.")

    distrib = degreedist(g2)
    distrib.show()
    nodecount = g2.vertices.count()
    print("Graph has " + str(nodecount) + " vertices.")

    out = filename.split("/")[-1]
    print("Writing distribution to file " + out + ".csv")
    distrib.toPandas().to_csv(out + ".csv")

# Otherwise, generate some random graphs.
else:
    print("Generating random graphs.")
    vschema = StructType([StructField("id", IntegerType())])
    eschema = StructType([StructField("src", IntegerType()),StructField("dst", IntegerType())])

    gnp1 = nx.gnp_random_graph(100, 0.05, seed=1234)
    gnp2 = nx.gnp_random_graph(2000, 0.01, seed=5130303)
    gnm1 = nx.gnm_random_graph(100,1000, seed=27695)
    gnm2 = nx.gnm_random_graph(1000,100000, seed=9999)

    todo = {"gnp1": gnp1, "gnp2": gnp2, "gnm1": gnm1, "gnm2": gnm2}
    for gx in todo:
        print("Processing graph " + gx)
        v = sqlContext.createDataFrame(sc.parallelize(todo[gx].nodes()), vschema)
        e = sqlContext.createDataFrame(sc.parallelize(todo[gx].edges()), eschema)
        g = simple(GraphFrame(v,e))
        distrib = degreedist(g)
        print("Writing distribution to file " + gx + ".csv")
        distrib.toPandas().to_csv(gx + ".csv")
