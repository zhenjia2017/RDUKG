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

## Evironment
Java: Jdk version needs to be 11 or above, e.g., OpenJDK-17.

## Data
 - The MKG dump for deployment is at [Google drive](https://drive.google.com/file/d/16blaKOpGwT-NruhDKwwqOktkwhCYBAbl/view?usp=drive_link). The total data size is around 1 GB. 
 - If you have any issues with downloading dataset, please contact Zhen Jia via mail: zjia@swjtu.edu.cn. 

- Follow the instructions at [link](https://neo4j.com/docs/operations-manual/5/installation/) to install Neo4J (We provide the instruction on Debian and Debian-based Linux systems).

  -    Adding the Debian repository
  ```
  wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
  echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
  sudo apt-get update
  ```
  -    Adding the Debian repository

  -    Install Neo4j Community Edition:
  ```
  sudo apt-get install neo4j
  ```

  -    Put the MKG dump in the */path/to/graph.dump/* for your configuration. 

  -    Input the URL **http://localhost:7474** in your browser to confirm if the Neo4j service is running and accessible.
      
 
## MKG Usage Examples

We provide a script **[DrugReview.py](mkg_usage/DrugReview.py)** showing how to connect and retrieve the MKG to verify patient's medication safety based on rules as use cases. 
 - Requirement: `py2neo` package.
     ```
     pip install py2neo
     ```

- `query_database` function: call the run method on the graph object to execute a query in the MKG. The query statement is written in Cypher, which is a declarative graph query language used by Neo4j.


- `drug_interactions` function: check for potential interactions between a set of drugs that a patient might be taking by using the DDI knowledge in the MKG.


- `allergy_review` function: check if there are any allergens in the drugs a user is taking.


-  `adverse_reaction_review` function: check for potential adverse reactions that a user might experience based on the drugs they are taking and a disease that they are suffering.


-  `duplicate_drug_review` function: check for potential duplicate or overlapping ingredients between different medications that a user might be taking.


-  `contraindication_review` function: check for contraindications between a list of drugs that a patient is taking and a specified disease.


-  `age_review` function: review whether the drugs a patient is taking are suitable for their age.


-  `special_population_review`: review whether the drugs a patient is taking are suitable for special populations, such as pregnant women, children, elderly people, or those with specific medical conditions.


-  `method_review` function: review whether the methods for the drugs a patient is taking are correct.


## Feedback
Any feedback is welcome! Please do not hesitate to contact us via mail: zjia@swjtu.edu.cn.

## License
The MKG is licensed under [MIT license](LICENSE).
