## Install powerlaw
#!pip install powerlaw
import pandas
import powerlaw

files = ['gnp1.csv', 'gnp2.csv', 'gnm1.csv', 'gnm2.csv', 'youtube.graph.small.csv', 'youtube.graph.large.csv', 'dblp.graph.small.csv', 'dblp.graph.large.csv', 'amazon.graph.small.csv', 'amazon.graph.large.csv']
for file in files:
    f  = pandas.read_csv(file)
    result = powerlaw.Fit(f['count'])
    if result.power_law.alpha >= 2 and result.power_law.alpha <= 3:
        print(file + " having gamma = " + str(result.power_law.alpha) + ' follows power law')