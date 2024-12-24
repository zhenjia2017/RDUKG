## DrugReviewSystem

Module to connect and retrieve the MKG to verify patient's medication safety based on rules.

### `query_database` function

**input:**

`query:` The cypher codes to run in the MKG.

**Description:**

This method calls the run method on the graph object to execute a query in the MKG. The query statement is written in Cypher, which is a declarative graph query language used by Neo4j.

**output:**

Return a list of dictionaries, where each dictionary represents a row of the query result.


### `drug_interactions` function

**input:**

`user_drugs`: IDs of drugs that patient will take, usually a list.


**Description:**

This method checks for potential interactions between a set of drugs that a patient might be taking by using the DDI knowledge in the MKG.

**output:**

Return if there are no potential interactions between any of the drugs. If the answer is false, return will be accompanied by a list of strings, where each string provides a warning message for each pair of drugs that may interact. 


### `allergy_review` function

**input:**

`user_drugs`: IDs of drugs that patient will take, usually a list.

`user_allergens`: the patient's allergen.

**Description:**

This method checks if there are any allergens in the drugs a user is taking.

**output:**

If any drugs containing allergens were found, the function returns a tuple (False, allergens_found). This indicates that the review did not pass, and the second element of the tuple is the list of drugs that contain allergens.


### `adverse_reaction_review` function

**input:**

`user_drugs`: IDs of drugs that patient will take, usually a list.

`disease`: A string, which represents a disease or health condition that the patient has or wants to avoid as a potential adverse reaction

**Description:**

This method checks for potential adverse reactions that a user might experience based on the drugs they are taking and a string of diseases.

**output:**

Return a boolean value representing that if one or more of the drugs can potentially cause an adverse reaction related the diseases. If the boolean is False,  return will be accompanied by a list of formatted strings, each indicating which drug might lead to which adverse reaction.



### `contraindication_review` function

**input:**

`user_drugs`: IDs of drugs that patient will take, usually a list.

`disease:`Contraindication that should be avoided.

**Description:**

This method checks for contraindications between a list of drugs that a patient is taking and a specified disease.

**output:**

Return a boolean value indicating whether the review has detected any contraindications (False if there are contraindications, True if not). If the boolean is False,  return will be accompanied by a list of drugs that have contraindications with the input disease.



### `age_review` function

**input:**

`user_drugs`: IDs of drugs that patient will take, usually a list.

`age:`Patient's age.

**Description:**

This method reviews whether the drugs a patient is taking are suitable for their age.

**output:**

Return a boolean value indicating whether the review has detected any drugs unsuitable for the user's age (False if there are such drugs, True if not). If the boolean is False,  return will be accompanied a list of drugs that are not suitable for the user's age.



### `special_population_review` function

**input:**

`user_drugs`: IDs of drugs that patient will take, usually a list.

`population:`A special population category or condition that the patient falls into.

**Description:**

This method reviews whether the drugs a patient is taking are suitable for special populations, such as pregnant women, children, elderly people, or those with specific medical conditions.

**output:**

Return a boolean value indicating whether the review has detected any drugs with special usage considerations for the specified populations (False if there are such drugs, True if not). If the boolean is False,  return will be accompanied a list of drugs that have special usage considerations for the specified populations.



### `method_review` function

**input:**

`user_drugs_methods`: A list of tuples, where each tuple contains two elements:

- The first element is a string representing the name of a drug (drug) that the patient is currently taking.
- The second element is a string representing the method that the patient is using for the specific drug. This could be terms like "oral", "intravenous", "topical", etc.

**Description:**

This method reviews whether the methods for the drugs a patient is taking are correct.

**output:**

Return a boolean value indicating whether the review has detected any drugs with incorrect methods(False if there are such drugs, True if not). If the boolean is False,  return will be accompanied a list of formatted messages indicating which drugs have incorrect methods 