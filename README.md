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
 - You need the MKG compressed file for deployment. We provide the MKG compressed file for deployment on Linux and Windows, respectively. You can choose one according to your requirements. 
 - The MKG for deployment on Linux is at [link](https://drive.google.com/file/d/19HMFE68t-6-hzyNUzKR71WP5CctP6cXN/view?usp=drive_link), for deployment on Windows is at [link](https://drive.google.com/file/d/1i0Go1ZaJp9Oy7GIqhnToxylw0zAkpPVe/view?usp=drive_link). 
If you have any issues with downloading dataset, please contact Zhen Jia via mail: zjia@swjtu.edu.cn. 
-  put the data in the */path/to/graph.dump/* for your configuration. The total data size is around 3 GB.

## Deployment
- Follow the instructions at [link](https://neo4j.com/docs/operations-manual/5/installation/) to install Neo4J (We provide the instruction on Debian and Debian-based Linux systems.
Adding the Debian repository
```
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
```

To install Neo4j Community Edition:
```
sudo apt-get install neo4j
```
- 
- Configure the Neo4j environment on Linux.
      
     - Navigate to the Neo4j bin directory:
       ```
       cd /path/to/neo4j/bin
       ```
     - Start the Neo4j service:
       ```
       neo4j start
       ``` 
     - If the service successfully started, you will see the similar output:
       ```      
        Active database: graph.db
        Directories in use:
          home:         /usr/local/neo4j/neo4j-community-3.5.11
          config:       /usr/local/neo4j/neo4j-community-3.5.11/conf
          logs:         /usr/local/neo4j/neo4j-community-3.5.11/logs
          plugins:      /usr/local/neo4j/neo4j-community-3.5.11/plugins
          import:       /usr/local/neo4j/neo4j-community-3.5.11/import
          data:         /usr/local/neo4j/neo4j-community-3.5.11/data
          certificates: /usr/local/neo4j/neo4j-community-3.5.11/certificates
          run:          /usr/local/neo4j/neo4j-community-3.5.11/run
        Starting Neo4j.
        Started neo4j (pid 150). It is available at http://0.0.0.0:7474/
        There may be a short delay until the server is ready.
        See /usr/local/neo4j/neo4j-community-3.5.11/logs/neo4j.log for current status.
       ``` 
    - You can use the following command to confirm whether the service is running: 
      ```
       neo4j status
      ``` 
    - You will see the similar output if the service is running:     
      ``` 
      Neo4j is running at pid 101291
      ``` 
 - Configure the Neo4j environment on Windows.
   
    - This computer → Properties (R) → Advanced System Settings → Environment Variables

    - Add variable **NEO4J_HOME** in the system variables, the value is the *folder* of the unzip data.

    - Add **%NEO4J_HOME%\bin** to path in the system variables.
   
    - Verify the Neo4j environment is setup successfully. Open cmd, input the command to start the Neo4j service:
   
      ```
       neo4j.bat console
       ```
   
    - The output shows as follows if the service starts successfully.

      ```
      INFO  ======== Neo4j 3.5.11 ========
      INFO  Starting...
      INFO  Bolt enabled on 127.0.0.1:7687.
      INFO  Started.
      INFO  Remote interface available at http://localhost:7474/
      ```
 
   - Input the URL **http://localhost:7474** in your browser to confirm if the Neo4j service is running and accessible.
   
 
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