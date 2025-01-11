# Medical Knowledge Graph Deployment and Usage

Description
------
This repository is for the [Medical Knowledge Graph (MKG)](https://link.springer.com/content/pdf/10.1007/s44230-022-00005-z.pdf) deployment and usage. 

For more details see our paper: [Medical Knowledge Graph to Promote Rational Drug Use: Model
Development and Performance Evaluation](https://link.springer.com/content/pdf/10.1007/s44230-022-00005-z.pdf) 

If you use this MKG, please cite:
```bibtex
@article{liao2022medical,
  title={Medical Knowledge Graph to Promote Rational Drug Use: Model Development and Performance Evaluation},
  author={Liao, Xiong and Liao, Meng and Guo, Andi and Luo, Xinran and Li, Ziwei and Chen, Weiyuan and Li, Tianrui and Du, Shengdong and Jia, Zhen},
  journal={Human-Centric Intelligent Systems},
  volume={2},
  number={1},
  pages={1--13},
  year={2022},
  publisher={Springer}
}
```

## Requirements
Java: The JDK version needs to be 11 or above, e.g., OpenJDK-17.

## Data
 - The MKG dump for deployment is at [Google Drive](https://drive.google.com/file/d/16blaKOpGwT-NruhDKwwqOktkwhCYBAbl/view?usp=drive_link). The total data size is around 1 GB. 
 - If you have any issues downloading the MKG dump, please contact Zhen Jia via mail: zjia@swjtu.edu.cn. 

## Deployment
- Follow the instructions at [link](https://neo4j.com/docs/operations-manual/5/installation/) to install Neo4J (We provide the instructions on Debian and Debian-based Linux systems).

  -    Adding the Debian repository
  ```
  wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
  echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
  sudo apt-get update
  ```

  -    Install Neo4j Community Edition:
  ```
  sudo apt-get install neo4j
  ```

  -    Put the MKG dump in the */path/to/graph.dump/* for your configuration. 

  -    Confirm if the Neo4j service is running and accessible, input the URL ** http://localhost:7474 ** in your browser.
      
 
## MKG Usage Examples

We provide a script **[DrugReview.py](mkg_usage/DrugReview.py)** that shows how to connect to and retrieve the MKG to verify a patient's medication safety based on rules and use cases. 
 - Requirement: `py2neo` package.
     ```
     pip install py2neo
     ```

- `query_database` function: call the run method on the graph object to execute a query in the MKG. The query statement is written in Cypher, a declarative graph query language used by Neo4j.


- `drug_interactions` function: check for potential interactions between a set of drugs a patient might take by using the DDI knowledge in the MKG.


- `allergy_review` function: check for any allergens in the drugs a user takes.


-  `adverse_reaction_review` function: check for potential adverse reactions that a user might experience based on the drugs they are taking and a disease that they are suffering.


-  `duplicate_drug_review` function: check for potential duplicate or overlapping ingredients between different medications a user might be taking.


-  `contraindication_review` function: check for contraindications between a list of drugs that a patient is taking and a specified disease.


-  `age_review` function: review whether the drugs a patient takes suit their age.


-  `special_population_review`: review whether the drugs a patient takes suit special populations, such as pregnant women, children, elderly people, or those with specific medical conditions.


-  `method_review` function: review whether the methods for the drugs a patient is taking are correct.


## Feedback
Any feedback is welcome! Please do not hesitate to contact us via mail: zjia@swjtu.edu.cn.

## License
The MKG is licensed under [MIT license](LICENSE).
