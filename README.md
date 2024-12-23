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

## Deployment

 - Configure the JAVA environment. Jdk version needs to be 11 or above.

 - Please contact [Zhen Jia](mailto:zjia@swjtu.edu.cn) for the neo4j with MKG data zip file "neo4j-community-3.5.11.zip" and unzip it. The data folder structure is as follows:

 - Configure the neo4j environment.

   (1) This computer → Properties (R) → Advanced System Settings → Environment Variables

   (2) Add variable **NEO4J_HOME** in the system variables, the value is the unzip path.

   (3) Add **%NEO4J_HOME%\bin** to path in the system variables.			 

 - After configuring the neo4j environment, test if you can successfully run MKG.

   (1) Open cmd, input **neo4j.bat console**. The following output should be achieved.

   ```
   2024-12-23 15:22:36.493+0000 WARN  You are using an unsupported version of the Java runtime. Please use Oracle(R) Java(TM) Runtime Environment 8, OpenJDK(TM) 8 or IBM J9.
   2024-12-23 15:22:36.512+0000 INFO  ======== Neo4j 3.5.11 ========
   2024-12-23 15:22:36.560+0000 INFO  Starting...
   WARNING: An illegal reflective access operation has occurred
   WARNING: Illegal reflective access by org.eclipse.collections.impl.utility.ArrayListIterate (file:/E:/neo4j-community-3.5.11/lib/eclipse-collections-9.2.0.jar) to field java.util.ArrayList.elementData
   WARNING: Please consider reporting this to the maintainers of org.eclipse.collections.impl.utility.ArrayListIterate
   WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
   WARNING: All illegal access operations will be denied in a future release
   2024-12-23 15:22:46.450+0000 INFO  Bolt enabled on 127.0.0.1:7687.
   2024-12-23 15:22:48.384+0000 INFO  Started.
   2024-12-23 15:22:49.527+0000 INFO  Remote interface available at http://localhost:7474/
   ```

   (2) Input http://localhost:7474 in your browser to check if the server is setup successfully.

## Feedback
Any feedback is welcome! Please do not hesitate to contact us via mail: zjia@swjtu.edu.cn.

## License
The MKG is licensed under [MIT license](LICENSE).