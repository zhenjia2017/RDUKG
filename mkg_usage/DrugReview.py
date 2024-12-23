from py2neo import Graph
import itertools
import re


class DrugReviewSystem:
    def __init__(self, uri):
        self.graph = Graph(uri)

    def close(self):
        self.graph.disconnect()

    def query_database(self, query, parameters=None):
        return self.graph.run(query, parameters=parameters).data()

    # 药物相互作用审查
    def drug_interactions(self, user_drugs):
        interactions = []
        drug_data = {}
        for drug in user_drugs:
            query1 = f"""
                    MATCH (d:`药品`)-[:相互作用*3]->(n:`药物`)
                    WHERE d.name = '{drug}'
                    RETURN collect(n.name) AS interactions
                    """
            query2 = f"""
                    MATCH (d:`药品`)-[:成分*0..3]->(n:`药物`)
                    WHERE d.name = '{drug}'
                    RETURN collect(n.name) AS components
                    """
            results1 = self.query_database(query1)
            results2 = self.query_database(query2)
            if results1 and results2:
                drug_data[drug] = {
                    'interactions': set(results1[0]['interactions']),
                    'components': set(results2[0]['components'])
                }

        for drug1, drug2 in itertools.combinations(user_drugs, 2):
            if drug_data[drug1]['components'] & drug_data[drug2]['interactions']:
                interactions.append((drug1, drug2))
            if drug_data[drug1]['interactions'] & drug_data[drug2]['components']:
                interactions.append((drug1, drug2))

        if interactions:
            return False, [f"**{pair[0]}**与**{pair[1]}**存在相互作用" for pair in interactions]
        else:
            return True, "无药物相互作用"

    # 过敏原审查
    def allergy_review(self, user_drugs, user_allergens):
        allergens_found = []
        drug_data = {}
        for drug in user_drugs:
            query = f"""
                    MATCH (d:`药品`)-[:成分*0..3]->(n:`药物`)
                    WHERE id(drug) = {drug}
                    RETURN collect(n.name) AS components
                    """
            results = self.query_database(query)
            if results:
                drug_data[drug] = set(results[0]['components'])

        for drug, components in drug_data.items():
            common_allergens = components & set(user_allergens)  # set intersection
            if common_allergens:
                allergens_found.append(drug)
                #allergens_found.extend([(drug, allergen) for allergen in common_allergens])

        if allergens_found:
            return False, allergens_found
            #return False, [f"**{pair[0]}**含有过敏原**{pair[1]}**" for pair in allergens_found]
        else:
            return True, "无过敏原"

    # 不良反应审查
    def adverse_reaction_review(self, user_drugs, disease):
        adverse_reaction = []
        drug_data = {}
        for drug in user_drugs:
            query = f"""
                    MATCH (d:`药品`)-[:不良反应*0..3]->(ds:`病症`)
                    WHERE d.name = '{drug}'
                    RETURN collect(ds.name) AS reactions
                    """
            results = self.query_database(query)
            if results:
                drug_data[drug] = set(results[0]['reactions'])

        for drug, reactions in drug_data.items():
            common_disease = reactions & set(disease)  # set intersection
            if common_disease:
                adverse_reaction.extend([(drug, dis) for dis in common_disease])

        if adverse_reaction:
            return False, [f"**{pair[0]}**可能会导致不良反应**{pair[1]}**" for pair in adverse_reaction]
        else:
            return True, "无不良反应"

    # 重复用药审查
    def duplicate_drug_review(self, user_drugs):
        interactions = []
        drug_data = {}
        for drug in user_drugs:
            query = f"""
                    MATCH (d:`药品`)-[:成分*0..3]->(n:`药物`)
                    WHERE d.name = '{drug}'
                    RETURN collect(n.name) AS components
                    """
            results = self.query_database(query)
            if results:
                drug_data[drug] = set(results[0]['components'])

        for drug1, drug2 in itertools.combinations(user_drugs, 2):
            common_components = drug_data[drug1] & drug_data[drug2]  # set intersection
            if common_components:
                interactions.append(((drug1, drug2), list(common_components)))

        if interactions:
            return False, [f"**{pair[0][0]}**与**{pair[0][1]}**存在相同成分**{pair[1]}**" for pair in interactions]
        else:
            return True, "无重复用药"

    # 禁忌症审查
    def contraindication_review(self, user_drugs, disease):
        contraindication = []
        drug_data = {}
        for drug in user_drugs:
            query = f"""
                    MATCH (drug:`药品`)-[:用药*0..2]->()-[:患有]->(ds)
                    WHERE id(drug) = $drug
                    RETURN collect(ds.name) AS contraindications
                    """
            results = self.query_database(query)
            if results:
                drug_data[drug] = set(results[0]['contraindications'])

        for drug, contraindications in drug_data.items():
            common_disease = contraindications & set(disease)  # set intersection
            if common_disease:
                contraindication.append(drug)
                #contraindication.extend([(drug, dis) for dis in common_disease])

        if contraindication:
            return False, contraindication
            #return False, [f"**{pair[0]}**有禁忌症**{pair[1]}**" for pair in contraindication]
        else:
            return True, "禁忌症审查通过"

    # 年龄审查
    def age_review(self, user_drugs, age):
        age_found = []
        for drug in user_drugs:
            query = f"""
                        MATCH p1=(drug:`药品`)-[:用药*2]->(fact:`知识组`)-[:用药]->(age:`人群`),p2=(fact)-[:用药结果]->(useResult:`用药结果级别`)
                        WHERE id(drug) = $drug AND (age.name CONTAINS '以上' or age.name CONTAINS '以下' or age.name CONTAINS '大于' or age.name CONTAINS '小于' or age.name =~ '.*\\\\d+(~|至)\\\\d+.*') and age.name CONTAINS '岁'
                        WITH p1,p2,age
                        RETURN
                        CASE
                        WHEN (age.name CONTAINS '以上' or age.name CONTAINS '大于') and (toInteger({age}) < toInteger(apoc.text.regexGroups(age.name, '\\\\d+')[0][0])) THEN 'pass'
                        WHEN (age.name CONTAINS '以下' or age.name CONTAINS '小于') and (toInteger({age}) > toInteger(apoc.text.regexGroups(age.name, '\\\\d+')[0][0])) THEN 'pass'
                        END
                        AS age_pass
                        """

            results = self.query_database(query, {'drug': drug})
            if results:
                age_pass = results[0]['age_pass']
                if age_pass != 'pass':
                    age_found.append(drug)

        if age_found:
            return False, age_found
            #return False, [f"**{pair[0]}**不适宜**{pair[1]}**岁使用" for pair in age_found]
        else:
            return True, ["年龄审查通过"]

    # 特殊人群审查
    def special_population_review(self, user_drugs, population):
        special_population = []
        drug_data = {}

        # 为每个用户提供的人群词创建一个模糊匹配的模式
        population_patterns = [f"(?i).*{pop}.*" for pop in population]  # 使用正则表达式，(?i)表示不区分大小写

        for drug in user_drugs:
            query = """
                    MATCH p1=(drug:`药品`)-[:用药*0..2]->(fact:`知识组`)-[:用药]->(crowd:`人群`),p2=(fact)-[:用药结果]->(useResult:`用药结果级别`)
                    WHERE id(drug) = $drug
                    WITH p1,p2,crowd
                    RETURN collect(crowd.name) AS populations
                    """
            results = self.query_database(query, {'drug': drug})
            if results:
                # 将数据库中的人群名称与提供的人群模式进行比较
                drug_populations = set(results[0]['populations'])
                for pattern in population_patterns:
                    for pop in drug_populations:
                        if re.search(pattern, pop, re.IGNORECASE):  # 进行模糊匹配
                            special_population.append(drug)
                            #special_population.append((drug, pop))

        if special_population:
            #return False, [f"**{pair[0]}**不适宜**{pair[1]}**使用" for pair in special_population]
            return False,special_population
        else:
            return True, ["特殊人群审查通过"]

    # 给药途径审查
    def method_review(self, user_drugs_methods):
        method_found = []
        drug_data = {}
        for item in user_drugs_methods:
            drug = item[0]
            method = item[1]

            query = f"""
                    MATCH (d:`药品`)-[:用药方法*0..3]->(a:`给药途径`)
                    WHERE d.name = '{drug}'
                    RETURN collect(a.name) AS methods
                    """
            results = self.query_database(query)
            if results:
                drug_data[drug] = set(results[0]['methods'])

        for item in user_drugs_methods:
            drug = item[0]
            method = item[1]
            if method not in drug_data.get(drug, set()):
                method_found.append((drug, method))

        if not method_found:
            return True, "给药途径审查通过"
        else:
            return False, [f"**{pair[0]}**给药途径**{pair[1]}**不正确" for pair in method_found]



if __name__ == "__main__":
    uri = "http://localhost:7474"
    system = DrugReviewSystem(uri)
    user_drugs = [41445, 85711, 86834, 3308407, 3308407,2981834]
    #user_drugs = ["氯雷他定片", "氨茶碱缓释片", "氧氟沙星氯化钠注射液", "复方妥英麻黄茶碱片", "丙硫异烟胺肠溶片"]
    user_drugs2 = ['来氟米特片']
    allergies = ["氯雷他定", "头孢"]
    disease = ["头痛", "咳嗽", "活动性消化溃疡"]
    population = ["儿童", "哺乳期", "孕妇"]
    user_drugs_methods = [["氧氟沙星氯化钠注射液", "口服"], ["氧氟沙星氯化钠注射液", "静脉缓慢滴注"]]
    age = 8
    # result, message = system.drug_interactions(user_drugs)
    # result, message = system.allergy_review(user_drugs, allergies)
    # result, message = system.adverse_reaction_review(user_drugs, disease)
    # result, message = system.duplicate_drug_review(user_drugs)
    # result, message = system.contraindication_review(user_drugs, disease)
    result, message = system.special_population_review(user_drugs, population)
    # result, message = system.method_review(user_drugs_methods)
    # result, message = system.age_review(user_drugs, age)
    print(message)
