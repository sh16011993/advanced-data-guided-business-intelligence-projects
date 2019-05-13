# Uncomment the following lines to install missing packages
# Install the packages
# install.packages('vars')
# Install pcalg package
# Option 1:
# Source: https://r-forge.r-project.org/R/?group_id=624
# install.packages("pcalg", repos="http://R-Forge.R-project.org")
# Option 2:
# install.packages("pcalg", dependencies = TRUE)
# source("http://bioconductor.org/biocLite.R")
# biocLite(c("graph", "RBGL", "Rgraphviz"))
# install.packages("gRain", dependencies=TRUE)

# Load the vars library 
library(vars)
library(pcalg)
# Read the input data 
input_data <- read.csv('data.csv')

# Build a VAR model 
# Select the lag order using the Schwarz Information Criterion with a maximum lag of 10 
VARselect(input_data, lag.max=10)
var_obj <- VAR(input_data, p=1)

# Extract the residuals from the VAR model 
residual_data <- residuals(var_obj)

# Check for stationarity using the Augmented Dickey-Fuller test 
apply(residual_data, 2, function(x) summary(ur.df(x, type="none")))
# The p-value for all the residuals of three variables indicates that there is evidence
# to reject the null hypothesis. Hence, the residuals follow a stationary pattern.

# Check whether the variables follow a Gaussian distribution  
apply(residual_data, 2, function(x) shapiro.test(x))
# Based on the Shapiro-Wilk test, we have evidence to reject the null hypothesis i.e., the 
# residuals follow a normal (Gaussian) distribution.

# Run the PC and LiNGAM algorithm in R as follows,

# PC Algorithm
suffStat<-list(C=cor(residual_data), n=nrow(residual_data))
pc_fit <- pc(suffStat, indepTest=gaussCItest, alpha=0.1, labels=colnames(residual_data), skel.method="original", verbose=TRUE)
plot(pc_fit, main="PC Output")

# LiNGAM Algorithm
lingam_fit <- LINGAM(residual_data, verbose=TRUE)
show(lingam_fit)