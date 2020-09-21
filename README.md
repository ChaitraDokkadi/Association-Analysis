# Association-Analysis
Investigated frequent itemsets from Gene Expressions dataset by implementing Principle Components Analysis and performing association analysis by Apriori Algorithm
## Steps to run PCA, SVD and t-SNE algorithm for given data in pca_a.txt file:
  1. Open cmd in current folder which contains PCA.py and pca_a.txt file
  2. Type the following command in the cmd:
		'python PCA.py pca_a.txt'
  3. The plots for PCA, SVD, t-SNE algorithm are generated as PCA_pca_a.png, SVD_pca_a.png, t-SNE_pca_a.png respectively in the current folder
## Steps to run Association analysis using Apriori algorithm for given data file with support and confidence:
  1. Open cmd in current folder which contains Association.py and associationruletestdata.txt file
  2. Type the following command in the cmd:
     Format:  'python Association.py [data file name] [support percentage] [confidence percentage]'
	 Example: 'python Association.py associationruletestdata.txt 50 70'
  3. The lengths of frequent itemsets and the count of rules generated are printed
  4. To get the rules generated for queries in the format of any of the three templates mentioned in the Template.pdf, enter the query in the cmd.
     Example: 'asso_rule.template1("RULE", "ANY", ['G59_Up'])'
  5. To quit the program in the cmd, enter 'exit' in the cmd  
## Example results from PCA, SVD, and t-SNE
1. PCA ![PCA-Img](https://github.com/ChaitraDokkadi/Association-Analysis/blob/master/Images/PCA_pca_a.png)
2. SVD ![SVD-Img](https://github.com/ChaitraDokkadi/Association-Analysis/blob/master/Images/SVD_pca_a.png)
3. PCA ![t-SNE-Img](https://github.com/ChaitraDokkadi/Association-Analysis/blob/master/Images/t-SNE_pca_a.png)

