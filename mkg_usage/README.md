## MKG Deployment

#### 1. Configure the JAVA environment. Jdk version needs to be 11 or above.

#### 2. Please contact [Zhen Jia](mailto:zjia@swjtu.edu.cn) for the neo4j with MKG data zip file "neo4j-community-3.5.11.zip" and unzip it. The data folder structure is as follows:

#### 3. Configure the neo4j environment.

   ##### (1) This computer → Properties (R) → Advanced System Settings → Environment Variables

   ##### (2) Add variable **NEO4J_HOME** in the system variables, the value is the unzip path.

   ##### (3) Add **%NEO4J_HOME%\bin** to path in the system variables.			 

#### 4. After configuring the neo4j environment, test if you can successfully run MKG.

  ##### (1)Open cmd, input **neo4j.bat console**. The following output should be achieved.

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

  ##### (2)Input http://localhost:7474 in your browser to check if the server is setup successfully.

