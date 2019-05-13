from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import operator
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams["backend"] = "TkAgg"

def main():
    conf = SparkConf().setMaster("local[2]").setAppName("Streamer")
    sc = SparkContext(conf=conf)
    sc.setLogLevel('ERROR')
    ssc = StreamingContext(sc, 10)   # Create a streaming context with batch interval of 10 sec
    ssc.checkpoint("checkpoint")

    pwords = load_wordlist("positive.txt")
    nwords = load_wordlist("negative.txt")
  
    counts = stream(ssc, pwords, nwords, 100)
    make_plot(counts)


def make_plot(counts):
    """
    Plot the counts for the positive and negative words for each timestep.
    Use plt.show() so that the plot will popup.
    """
    # YOUR CODE HERE
    # Plotting the points
    pos = []
    neg = []
    time = []
    i = 0
    for val in counts:
        p = val[1]
        n = val[0]
        pos.append(p[1])
        neg.append(n[1])
        i = i + 1
        time.append(i)  
    plt.plot(time, pos, color='b', linestyle='--', marker='o', label = "Positive")
    plt.plot(time, neg, color='r', linestyle='-',  marker='o', label = "Negative")
  
    # Adding legend 
    plt.legend(loc = "upper right")

    # Adding labels
    plt.xlabel('Time')
    plt.ylabel('Count')

    # Plot Title
    plt.title('Graph for Positive and Negative Tweets')

    # Saving the plot
    plt.savefig('./plot.png', format = 'png') 
  
    # Showing the plot 
    plt.show() 


def load_wordlist(filename):
    """ 
    This function should return a list or set of words from the given filename.
    """
    # YOUR CODE HERE
    f = open(filename)
    unique_words_set = set()
    for line in f:
        word = line.strip()
        unique_words_set.add(word)
    f.close()
    return(unique_words_set)


def checkWordCategory(word, pwords, nwords):
    if word in pwords:
        return(('positive', 1))
    if word in nwords:
        return(('negative', 1))
    else:
        return(('negative', 0))
        
def updateFunction(newValues, runningCount):
    if runningCount is None:
        runningCount = 0
    return sum(newValues, runningCount) 

def stream(ssc, pwords, nwords, duration):
    kstream = KafkaUtils.createDirectStream(ssc, topics = ['twitterstream'], kafkaParams = {"metadata.broker.list": 'localhost:9092'})
    tweets = kstream.map(lambda x: x[1])
    
    # Each element of tweets will be the text of a tweet.
    # You need to find the count of all the positive and negative words in these tweets.
    # Keep track of a running total counts and print this at every time step (use the pprint function).
    # YOUR CODE HERE
    
    words_list = tweets.flatMap(lambda tweet: tweet.split(" "))
    modified_words_list = words_list.map(lambda j: checkWordCategory(j, pwords, nwords))  
    #words_list.pprint()
    #modified_words_list.pprint()
    modified_words_list_count = modified_words_list.reduceByKey(lambda x, y: x + y)
    #modified_words_list_count.pprint()
 
    # Let the counts variable hold the word counts for all time steps
    # You will need to use the foreachRDD function.
    # For our implementation, counts looked like:
    #   [[("positive", 100), ("negative", 50)], [("positive", 80), ("negative", 60)], ...]
    counts = []
    total_counts = modified_words_list_count.updateStateByKey(updateFunction)
    #modified_words_list_count.pprint()
    total_counts.pprint()
    modified_words_list_count.foreachRDD(lambda t,rdd: counts.append(rdd.collect()))
    
    ssc.start()                         # Start the computation
    ssc.awaitTerminationOrTimeout(duration)
    ssc.stop(stopGraceFully=True)

    return counts


if __name__=="__main__":
    main()
