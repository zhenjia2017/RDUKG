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

## MKG Data
 - The MKG dump for deployment is at [Google Drive](https://drive.google.com/file/d/16blaKOpGwT-NruhDKwwqOktkwhCYBAbl/view?usp=drive_link).
 - The total data size is around 1 GB.

## Linux installation(Ubuntu)

This is an operational manual for deploying Neo4j on Ubuntu. If you want to learn more information or deploy it on other systems, you can refer to [here](https://neo4j.com/docs/operations-manual/current/installation/linux/).


### Java prerequisites

Neo4j 5 requires the Java 17 runtime.

1.List all your installed versions of Java:

```bash
update-java-alternatives --list
```

1.1 If Java 17 is not included in the results, execute the following command to install OpenJDK 17:

```bash
sudo apt install openjdk-17-jre
```

1.2 Set it as the default by replacing `<java17name>` with its name:

```bash
sudo update-java-alternatives --jre --set <java17name>
```

2.Identify your Java 17 version:

```bash
java -version
```



###  Installation

1.To use the repository for generally available versions of Neo4j, run:

```bash
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/neotechnology.gpg

echo 'deb [signed-by=/etc/apt/keyrings/neotechnology.gpg] https://debian.neo4j.com stable latest' | sudo tee -a /etc/apt/sources.list.d/neo4j.list

sudo apt-get update
```

2.Install neo4j community edition:

```bash
sudo apt-get install neo4j=1:5.26.1
```

3.Starting the service automatically on system start:

```bash
sudo systemctl enable neo4j
```

4.Then you can run the following command to controlling the service:

```
sudo neo4j {start|stop|restart}
```



### Start Neo4j

1.Modify the configuration file, located at `/etc/neo4j/neo4j.conf`:

```.cofig
initial.dbms.default_database=graph
```

2.Restart neo4j service:

```bash
sudo neo4j restart
```

3.Open [http://localhost:7474](http://localhost:7474/) in your web browser.

4.Connect using the username `neo4j` with your password or the default password `neo4j`. You will then be prompted to change the password. The default database is `graph` which you set in step 1.



### Import database

1.Stop neo4j service:

```bash
sudo neo4j stop
```

2.Create a `dump` folder  at `$NEO4J_HOME/` :

```bash
cd <NEO4J_HOME>
sudo mkdir dump
```

3.Place `graph.dump` inside it, run:

```bash
neo4j-admin database load --from-path=dump graph --overwrite-destination=true
```

4.Start neo4j service, then you can use this database:

```bash
sudo neo4j start
```



### APOC

APOC (Awesome Procedures on Cypher) is an add-on library for Neo4j that provides hundreds of procedures and functions adding a lot of useful functionality. You can find more information in [here](https://neo4j.com/labs/apoc/).

APOC can be installed by moving the APOC jar file from the `$NEO4J_HOME/labs` directory to the `$NEO4J_HOME/plugins` directory and restarting Neo4j.



## MKG Usage Examples

We provide a script **[drug_review_system.py](mkg_usage/drug_review_system.py)** that shows how to connect to and retrieve the MKG to verify a patient's medication safety based on rules and use cases. 
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
Any feedback is welcome! If you have any issues downloading or deploying the MKG, please do not hesitate to contact us via mail: zjia@swjtu.edu.cn.

## License
The MKG is licensed under [MIT license](LICENSE).
