import sys
import os
import numpy as np
import pandas as pd
from itertools import combinations 
import time

file_name = sys.argv[1]
support = int(sys.argv[2])
confidence = int(sys.argv[3])

# file_name = 'associationruletestdata.txt'
# support = 50
# confidence = 70

data = pd.read_csv(file_name, sep='\t', lineterminator='\n', header=None)
unique_item_set = set()
i = 0
for column in data.columns[:-1]:
    data[column] = 'G' + str(column+1) + "_" + data[column].astype(str)
    unique_item_set = unique_item_set | set(data[column].unique())

unique_item_set = unique_item_set | set(data.iloc[:,-1])

data_set = []
for row_index in range(len(data)):
    data_set.append(set(data.iloc[row_index]))

support = (support/100)*len(data)
confidence = confidence/100

association_rules = pd.DataFrame(columns=['RULE','HEAD','BODY','SUPPORT','CONFIDENCE'])

all_frequent_list_map = {}
max_length_frequent_itemsets = 0

frequent_itemset = set()
for unique_item in unique_item_set:
    current_item_count = 0
    for data_item in data_set:
        current_item_count = (current_item_count+1) if(unique_item in data_item) else int(current_item_count) 
        if (current_item_count<support):
            continue
        frequent_itemset.add(str(unique_item))
        list_of_items = list()
        list_of_items.append(str(unique_item))
#         print(set(list_of_items))
        all_frequent_list_map[str(set(list_of_items))] = current_item_count
		
start_time = time.time()

no_of_data_columns = len(data.columns)
current_frequent_list = list(map(lambda elem:[elem], list(frequent_itemset))) 
current_frequent_list.sort()
visited_rules = []
print("number of length-1 frequent itemsets: "+str(len(frequent_itemset)))


max_length_frequent_itemsets = 0
for i in range(len(frequent_itemset)):
    new_frequent_list = []
    for j in range(len(current_frequent_list)):
        for k in range(j+1, len(current_frequent_list)):
            merged_list = list(set(current_frequent_list[j]).union(set(current_frequent_list[k])))
            if (len(merged_list) == len(current_frequent_list[j])+1):
                temp_merged_list = list(merged_list)
                temp_merged_list.sort()
                subsets_of_merged_list = [set(item) for item in list(combinations(set(temp_merged_list), len(current_frequent_list[j])))]
                current_item_count = 0
                
                for item in data_set:
                    current_item_count = (current_item_count+1) if(set(merged_list).issubset(item)) else int(current_item_count) 
                all_frequent_list_map[str(set(temp_merged_list))] = current_item_count
                if (current_item_count<support):
                    continue
                subset_count = 0
                for current_subset_item in subsets_of_merged_list:
                    for current_frequent_item in current_frequent_list:
                        current_frequent_set = set(current_frequent_item)
                        if (current_subset_item.issubset(current_frequent_set)):
                            subset_count += 1
                            break
                    if subset_count == len(subsets_of_merged_list):
                        break
                if (subset_count == len(subsets_of_merged_list)):
                    concatenated_list = ''.join(temp_merged_list)
                    if (concatenated_list in visited_rules):
                        continue
                    visited_rules.append(concatenated_list)
                    new_frequent_list.append(temp_merged_list)
                    pruned_rules = []
                    for merged_list_index in reversed(range(len(temp_merged_list))):
                        if(len(temp_merged_list)<=(merged_list_index+1)):
                            continue
                        data_combinations = [set(item) for item in list(combinations(temp_merged_list,merged_list_index+1))]
                        for current_subset_item in data_combinations:
                            y=list(current_subset_item)
                            y.sort()
                            prune_list_concatenation = ''.join(y)
                            low_confidence = False
                            for pruned_rule in pruned_rules:
                                if prune_list_concatenation in pruned_rule:
                                    low_confidence = True
                            if low_confidence:
                                break
                            current_confidence=all_frequent_list_map[str(set(temp_merged_list))]/all_frequent_list_map[str(set(y))]
                            if(current_confidence>confidence):
                                association_rules.loc[len(association_rules)]=pd.Series({'RULE': str(temp_merged_list), 'HEAD': str(current_subset_item), 'BODY': str(set(temp_merged_list).difference(current_subset_item)), 'SUPPORT': all_frequent_list_map[str(set(temp_merged_list))]/len(data), 'CONFIDENCE': current_confidence})
                            else:
                                pruned_rules.append(prune_list_concatenation)
    if (len(new_frequent_list) == 0):
        break
    new_frequent_list = list(map(list, set(map(frozenset, new_frequent_list))))
    current_frequent_list = new_frequent_list
    print("number of length-"+str(i+2),"frequent itemsets: "+str(len(current_frequent_list)))
    max_length_frequent_itemsets = i+2    

association_rules.drop_duplicates()
# print('time taken to get frequent itemsets: ', (time.time() - start_time), ' seconds')
print(str(len(association_rules)) + " rules are generated. \n")
association_rules.to_csv('AssociationRules.csv', index = None)

def queryTemplate1(query, result):
    if (query[0] == 'RULE' and query[1] == 'ANY'):
        for query_item in query[2]:
            result = result.append(association_rules[association_rules['RULE'].str.contains(query_item)])
    elif (query[0] == 'RULE' and query[1] == 'NONE'):
        for query_item in query[2]:
            result = result.append(association_rules[~association_rules['RULE'].str.contains(query_item)])
    elif (query[0] == 'RULE' and query[1] >= 1):
        length_combinations = [set(item) for item in list(combinations(set(query[2]),query[1]))]
        for combination in length_combinations:
            temp_result = pd.DataFrame(data=None, columns=association_rules.columns)
            combination_list = list(combination)
            positive_result = association_rules['RULE'].str.contains(combination_list[0])
            for i in range(1, len(combination_list)):
                positive_result = positive_result & association_rules['RULE'].str.contains(combination_list[i]) 
            temp_result = temp_result.append(association_rules[positive_result])
            remaining_combination = set(query[2]).difference(combination)
            remaining_combination = list(remaining_combination)
            if (len(remaining_combination) < 1):
                result = result.append(temp_result)
                continue
            negative_result = ~temp_result['RULE'].str.contains(remaining_combination[0])
            for i in range(1, len(remaining_combination)):
                negative_result = negative_result & ~temp_result['RULE'].str.contains(remaining_combination[i])
            temp_result = temp_result[negative_result]
            result = result.append(temp_result)
    elif (query[0] == 'HEAD' and query[1] == 'ANY'):
        for query_item in query[2]:
            result = result.append(association_rules[association_rules['HEAD'].str.contains(query_item)])
    elif (query[0] == 'HEAD' and query[1] == 'NONE'):
        for query_item in query[2]:
            result = result.append(association_rules[~association_rules['HEAD'].str.contains(query_item)])
    elif (query[0] == 'HEAD' and query[1] >= 1):
        length_combinations = [set(item) for item in list(combinations(set(query[2]),query[1]))]
        for combination in length_combinations:
            temp_result = pd.DataFrame(data=None, columns=association_rules.columns)
            combination_list = list(combination)
            positive_result = association_rules['HEAD'].str.contains(combination_list[0])
            for i in range(1, len(combination_list)):
                positive_result = positive_result & association_rules['HEAD'].str.contains(combination_list[i]) 
            temp_result = temp_result.append(association_rules[positive_result])
            remaining_combination = set(query[2]).difference(combination)
            remaining_combination = list(remaining_combination)
            if (len(remaining_combination) < 1):
                result = result.append(temp_result)
                continue
            negative_result = ~temp_result['HEAD'].str.contains(remaining_combination[0])
            for i in range(1, len(remaining_combination)):
                negative_result = negative_result & ~temp_result['HEAD'].str.contains(remaining_combination[i])
            temp_result = temp_result[negative_result]
            result = result.append(temp_result)
    elif (query[0] == 'BODY' and query[1] == 'ANY'):
        for query_item in query[2]:
            result = result.append(association_rules[association_rules['BODY'].str.contains(query_item)])
    elif (query[0] == 'BODY' and query[1] == 'NONE'):
        for query_item in query[2]:
            result = result.append(association_rules[~association_rules['BODY'].str.contains(query_item)])
    elif (query[0] == 'BODY' and query[1] == 1):
        length_combinations = [set(item) for item in list(combinations(set(query[2]),query[1]))]
        for combination in length_combinations:
            temp_result = pd.DataFrame(data=None, columns=association_rules.columns)
            combination_list = list(combination)
            positive_result = association_rules['BODY'].str.contains(combination_list[0])
            for i in range(1, len(combination_list)):
                positive_result = positive_result & association_rules['BODY'].str.contains(combination_list[i]) 
            temp_result = temp_result.append(association_rules[positive_result])
            remaining_combination = set(query[2]).difference(combination)
            remaining_combination = list(remaining_combination)
            if (len(remaining_combination) < 1):
                result = result.append(temp_result)
                continue
            negative_result = ~temp_result['BODY'].str.contains(remaining_combination[0])
            for i in range(1, len(remaining_combination)):
                negative_result = negative_result & ~temp_result['BODY'].str.contains(remaining_combination[i])
            temp_result = temp_result[negative_result]
            result = result.append(temp_result)
    return result

def queryTemplate2(query, result):
    if (query[0] == 'RULE'):
        result = result.append(association_rules[association_rules['RULE'].str.count(',')+1>=query[1]])
    elif (query[0] == 'HEAD'):
        result = result.append(association_rules[association_rules['HEAD'].str.count(',')+1>=query[1]])
    elif (query[0] == 'BODY'):
        result = result.append(association_rules[association_rules['BODY'].str.count(',')+1>=query[1]])
    return result

def queryTemplate3(query, result):
    if (query[0] == '1or1'):
        result = result.append(queryTemplate1(query[1:4], result))
        result = result.append(queryTemplate1(query[4:7], result))
    elif (query[0] == '1and1'):
        result = pd.merge(queryTemplate1(query[1:4], result), queryTemplate1(query[4:7], result), how='inner')
    elif (query[0] == '1or2'):
        result = result.append(queryTemplate1(query[1:4], result))
        result = result.append(queryTemplate2(query[4:6], result))
    elif (query[0] == '1and2'):
        result = pd.merge(queryTemplate1(query[1:4], result), queryTemplate2(query[4:6], result), how='inner')
    elif (query[0] == '2or2'):
        result = result.append(queryTemplate2(query[1:3], result))
        result = result.append(queryTemplate2(query[3:5], result))
    elif (query[0] == '2and2'):
        result = pd.merge(queryTemplate2(query[1:3], result), queryTemplate2(query[3:5], result), how='inner')
    return result.drop_duplicates()

while(True):
    result = pd.DataFrame(data=None, columns=association_rules.columns)
    query = input('Enter new query: ')
    if(query == "exit"):
        break
    elif (query.startswith('asso_rule.template1')):
        query= query.strip('asso_rule.template1')
        query = eval(query)
        result = queryTemplate1(query, result)
    elif (query.startswith('asso_rule.template2')):
        query= query.strip('asso_rule.template2')
        query = eval(query)
        result = queryTemplate2(query, result)
    elif (query.startswith('asso_rule.template3')):
        query= query.strip('asso_rule.template3')
        query = eval(query)
        result = queryTemplate3(query, result)
    else:
        print('Invalid query. \n')
        continue
    print(str(len(result)) + " rules are generated for the given query.\n")
#     print(result)