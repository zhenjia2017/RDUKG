# Medical Knowledge Graph Deployment and Usage

Description
------
This repository is for the [MKG](https://link.springer.com/content/pdf/10.1007/s44230-022-00005-z.pdf) deployment and usage. 

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
Java environment with the JDK version 11 or later.

## Data
 - You need the Neo4j medical knowledge graph data file ("neo4j-community-3.5.11.zip") for deployment. You can download from [here](https://pan.baidu.com/s/1UWaQqnZHuUMbbqeYY8kZuQ). The extraction code is:
    ```
   drkg
    ```
   If you have any issue with downloading, please contact [Zhen Jia](mail to:zjia@swjtu.edu.cn).
-  Unzip the data and put it in the *folder* for your configuration. The total data size is around 2 GB.

## Deployment
 - Configure the Neo4j environment on Windows.
   
    - This computer → Properties (R) → Advanced System Settings → Environment Variables

    - Add variable **NEO4J_HOME** in the system variables, the value is the *folder* of the unzip data.

    - Add **%NEO4J_HOME%\bin** to path in the system variables.
   
    - Verify the Neo4j environment is setup successfully. Open cmd, input the follow command to start the Neo4j service:
   
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
 
   - Input http://localhost:7474 in your browser to confirm if the Neo4j service is running and accessible.
   
  - Configure the Neo4j environment on Linux.
      
     - Edit the shell configuration file:
       ```
       sudo nano /etc/environment
       ```

     - Add a line to define the NEO4J_HOME variable. Replace **/path/to/neo4j** with the actual folder of Neo4j:
       ```
       export NEO4J_HOME=/path/to/neo4j
       ```

     - Add **NEO4J_HOME/bin** to the PATH variable:
       ```
       export PATH=$NEO4J_HOME/bin:$PATH
       ```
     - Restart the shell or reboot the system:
       ```
       source /etc/environment
       ```
     - Verify the Neo4j environment is setup successfully. Use **systemctl** to check if the Neo4j service is running:
       ```
       sudo systemctl status neo4j
       ```
       If it says "active (running)", the service is up. If not, you can start it with:
       ```
       sudo systemctl start neo4j
       ```

## Feedback
Any feedback is welcome! Please do not hesitate to contact us via mail: zjia@swjtu.edu.cn.

## License
The MKG is licensed under [MIT license](LICENSE).