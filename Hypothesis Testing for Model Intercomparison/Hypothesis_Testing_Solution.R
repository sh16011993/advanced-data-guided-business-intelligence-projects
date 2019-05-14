# ========================================
# Multiple Hypothesis Testing
# Part 1: K-fold Cross-Validation Paired t-Test
# Part 2: Analysis of Variance (ANOVA) Test
# Part 3: Wilcoxon Signed Rank test
# ========================================

# Uncomment for the first-time install
#install.packages("cvTools", dependencies = TRUE)
#install.packages("C50", dependencies = TRUE)
#install.packages("e1071", dependencies = TRUE)
# Load the required R packages
library(cvTools)
library(C50)
library(e1071)
library(kernlab)

# Set working directory to source file location
# Session -> Set Working Directory -> To Source File Location

# **********************************************
# Part 1: K-fold Cross-Validation Paired t-Test
# *****************************************

# Load the iris data set
iris_data <- read.table('./datasets/Iris_data.txt', sep=',', header=F)
k <- 10

# Randomize the data and perform 10-fold Cross-Validation
# See ?sample and ?cvFolds
iris_folds <- cvFolds(n=nrow(iris_data), K=k, type="random")

# Use the training set to train a C5.0 decision tree and Support Vector Machine


# Make predictions on the test set and calculate the error percentages made by both the trained models
x_dt <- array(0, k)
x_svm <- array(0, k)

for(i in 1:k){
  idx_per_fold <- cbind(iris_folds$which, iris_folds$subsets)
  test_idx <- idx_per_fold[idx_per_fold[, 1]==i, 2]
  
  # Print the test_idx and then generate the training and testing sets
  train_data <- iris_data[-test_idx, ]
  test_data <- iris_data[test_idx, ]

  dt_obj <- C5.0(x=train_data[, -5], y=train_data[, 5])  
  svm_obj <- ksvm(V5 ~., data=train_data)

  dt_pred <- predict(dt_obj, test_data[, -5])
  svm_pred <- predict(svm_obj, test_data[, -5])
  
  x_dt[i] <- sum(table(dt_pred, test_data[, 5])) - sum(diag(table(dt_pred, test_data[, 5])))
  x_svm[i] <- sum(table(svm_pred, test_data[, 5])) - sum(diag(table(svm_pred, test_data[, 5])))
}

# Perform K-fold Cross-Validation Paired t-Test to compare the means of the two error percentages
t.test(x_dt, x_svm, paired=TRUE)

# *****************************************
# Part 2: Analysis of Variance (ANOVA) Test
# *****************************************

# Load the Breast Cancer data set 
breast_cancer_data <- read.table('./datasets/Wisconsin_Breast_Cancer_data.txt', sep=',', header=F, row.names=1)
N <- nrow(breast_cancer_data)
k <- 10

# Randomize the data and perform 10-fold Cross-Validation
# See ?sample and ?cvFolds
all_folds <- cvFolds(n=N, K=k, type="random")

# Use the training set to train following classifier algorithms
# 	1. C5.0 decision tree (see ?C5.0 in C50 package)
# 	2. Support Vector Machine (see ?ksvm in kernlab package)
# 	3. Naive Bayes	(?naiveBayes in e1071 package) 
# 	4. Logistic Regression (?glm in stats package) 

# Make predictions on the test set and calculate the error percentages made by the trained models

x_dt <- array(0, k)
x_svm <- array(0, k)
x_nb <- array(0, k)

classifier <- c(rep("DT", k), rep("SVM", k), rep("NB", k))

for(i in 1:k){
  idx_per_fold <- cbind(all_folds$which, all_folds$subsets)
  test_idx <- idx_per_fold[idx_per_fold[, 1]==i, 2]
  
  # Print the test_idx and then generate the training and testing sets
  train_data <- breast_cancer_data[-test_idx, ]
  test_data <- breast_cancer_data[test_idx, ]

  dt_obj <- C5.0(x=train_data[, -1], y=train_data[, 1])  
  svm_obj <- ksvm(V2 ~. , data = train_data)
  nb_obj <- e1071::naiveBayes(x=train_data[, -1], y=train_data[, 1])
  
  dt_pred <- predict(dt_obj, test_data[, -1])
  svm_pred <- predict(svm_obj, test_data[, -1])
  nb_pred <- predict(nb_obj, test_data[, -1])
  
  x_dt[i] <- sum(table(dt_pred, test_data[, 1])) - sum(diag(table(dt_pred, test_data[, 1])))
  x_svm[i] <- sum(table(svm_pred, test_data[, 1])) - sum(diag(table(svm_pred, test_data[, 1])))
  x_nb[i] <- sum(table(nb_pred, test_data[, 1])) - sum(diag(table(nb_pred, test_data[, 1])))
}

# Compare the performance of the different classifiers using ANOVA test (see ?aov)
errors <- c(x_dt, x_svm, x_nb)

X <- data.frame(errors, classifier)

plot(errors~classifier, data=X)

aov_obj <- aov(errors~classifier, data=X)
summary(aov_obj)

# *****************************************
# Part 3: Wilcoxon Signed Rank test
# *****************************************

# Load the following data sets,
# 1. Iris 
iris_data <- read.table('./datasets/Iris_data.txt', sep=',', header=F)

# 2. Ecoli 
ecoli_data <- read.csv('./datasets/Ecoli_data.csv', header=F, row.names=1)

# 3. Wisconsin Breast Cancer
breast_cancer_data <- read.table('./datasets/Wisconsin_Breast_Cancer_data.txt', sep=',', header=F, row.names=1)

# 4. Glass
glass_data <- read.table('./datasets/Glass_data.txt', sep=',', header=F, row.names=1)

# 5. Yeast
yeast_data <- read.csv('./datasets/Yeast_data.csv', header=F)
yeast_data <- yeast_data[, -1]

# Randomize the data and perform 10-fold Cross-Validation
# See ?sample and ?cvFolds

iris_all_folds <- cvFolds(n=nrow(iris_data), K=k, type="random")
ecoli_all_folds <- cvFolds(n=nrow(ecoli_data), K=k, type="random")
breast_cancer_all_folds <- cvFolds(n=nrow(breast_cancer_data), K=k, type="random")
glass_all_folds <- cvFolds(n=nrow(glass_data), K=k, type="random")
yeast_all_folds <- cvFolds(n=nrow(yeast_data), K=k, type="random")

# Use the training set to train following classifier algorithms
# 	1. C5.0 decision tree (see ?C5.0 in C50 package)
# 	2. Support Vector Machine (see ?ksvm in kernlab package)

# Make predictions on the test set and calculate the error percentages made by the trained models
buildModel <- function(k, folds, data, classifiers='FLAG', response_idx){
  x_dt <- array(0, k)
  x_svm <- array(0, k)
  x_nb <- array(0, k)
  x_glm <- array(0, k)

  for(i in 1:k){
    idx_per_fold <- cbind(folds$which, folds$subsets)
    test_idx <- idx_per_fold[idx_per_fold[, 1]==i, 2]
    
    train_data <- data[-test_idx, ]
    test_data <- data[test_idx, ]
    
    dt_obj <- C5.0(x=train_data[, -response_idx], 
                   y=as.factor(train_data[, response_idx]))  
    svm_obj <- ksvm(x = train_data [, -response_idx],
                    y=as.factor(train_data[, response_idx]))
    
    dt_pred <- predict(dt_obj, test_data[, -response_idx])
    svm_pred <- predict(svm_obj, test_data[, -response_idx])
    
    x_dt[i] <- sum(diag(table(dt_pred, test_data[,response_idx])))/sum(table(dt_pred, test_data[, response_idx]))
    x_svm[i] <- sum(diag(table(svm_pred, test_data[,response_idx])))/sum(table(svm_pred, test_data[, response_idx]))
    
  }
  return(list(x_dt, x_svm))
}

accuracy_1 <- buildModel(k, iris_all_folds, iris_data, response_idx=5)
accuracy_2 <- buildModel(k, ecoli_all_folds, ecoli_data[, -4], response_idx=7)
accuracy_3 <- buildModel(k, breast_cancer_all_folds, breast_cancer_data, response_idx=1)
accuracy_4 <- buildModel(k, glass_all_folds, glass_data, response_idx=10)
accuracy_5 <- buildModel(k, yeast_all_folds, yeast_data, response_idx=9)

# Compare the performance of the different classifiers using Wilcoxon Signed Rank test (see ?wilcox.test)
dt_acc <- array(0, 5)
svm_acc <- array(0, 5)

dt_acc[1] <- mean(accuracy_1[[1]])
dt_acc[2] <- mean(accuracy_2[[1]])
dt_acc[3] <- mean(accuracy_3[[1]])
dt_acc[4] <- mean(accuracy_4[[1]])
dt_acc[5] <- mean(accuracy_5[[1]])

svm_acc[1] <- mean(accuracy_1[[2]])
svm_acc[2] <- mean(accuracy_2[[2]])
svm_acc[3] <- mean(accuracy_3[[2]])
svm_acc[4] <- mean(accuracy_4[[2]])
svm_acc[5] <- mean(accuracy_5[[2]])

wilcox.test(dt_acc, svm_acc)