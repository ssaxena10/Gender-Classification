# Gender-Classification

In this project, four celebrities with maximum followers are chosen - Taylor Swift, Justin Bieber, Jimmy Fallon & Rihanna. The aim of this project is to classify followers into male and female based on the tweets using US census data. Tasks performed are as follows :

Collect -
This script will establish twitter connection so as to extract followers of the celebrities mentioned above. Due to rate limit, few restrictions were applied. Followers per celebrity are limited to 5000 and maximum total tweets are limited to 1500. A networkx graph was created and saved for its use in clustering.

Cluster -
In this step, community detection will be implemented on the networkx graph created above. Girvan-Newman algorithm will be used on the celebrity and their followers' graph. The communities detected based on Girvan-Newman provides two clusters. Cluster0 shows three celebrities which do have quite a few followers in common. They are Jimmy Fallon, Justin Bieber, and Rihanna. Taylor Swift does not have many followers in common with others as mentioned above. This scripts run on a small sample and shows how people may fall in different communities. 

Classify -
This script will be used to classify the followers as male or female based on their tweets using US census data. The tweets loaded were labeled based on gender using the census data and a training set was then created for the classifier. Then a feature matrix was created from tokens and vocabulary list and with this feature matrix and labeled data, a logistic regression model was built. The model was then trained on the tweets and it was then tested. As a result, the model successfully predicts the gender of the followers.
