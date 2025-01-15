from neo4j import GraphDatabase
import itertools
import re


class DrugReviewSystem:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query_database(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]
        
    # 药物相互作用审查
    def drug_interactions(self, user_drugs):
        # 检查user_drugs是否为空
        if not user_drugs:
            return False, ["缺少相关数据"]

        if len(user_drugs) == 1:
            return True, ["药物相互作用审查通过"]

        interactions = []
        drug_data = {}
        for drug in user_drugs:
            query1 = f"""
                    MATCH (d:`药品`)-[:相互作用*3]->(n:`药物`)
                    WHERE d.name = '{drug}'
                    RETURN collect(n.name) AS interactions
                    """
            query2 = f"""
                    MATCH (d:`药品`)-[:成分*3]->(n:`药物`)
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
                common_components = drug_data[drug1]['components'] & drug_data[drug2]['interactions']
                interactions.append((drug1, drug2, "components", list(common_components)))
            if drug_data[drug1]['interactions'] & drug_data[drug2]['components']:
                common_interactions = drug_data[drug1]['interactions'] & drug_data[drug2]['components']
                interactions.append((drug1, drug2, "interactions", list(common_interactions)))

        # 根据检查结果返回相应的消息
        if interactions:
            messages = []
            for interaction in interactions:
                drug1, drug2, interaction_type, common_elements = interaction
                if interaction_type == "components":
                    messages.append(f"**{drug1}**的成分**{common_elements[0]}**与**{drug2}**有相互作用")
                elif interaction_type == "interactions":
                    messages.append(f"**{drug2}**的成分**{common_elements[0]}**与**{drug1}**有相互作用")
            return False, messages
        else:
            return True, ["药物相互作用审查通过"]

    # 过敏原审查
    def allergy_review(self, user_drugs, user_allergens):
        # 检查user_drugs是否为空
        if not user_drugs:
            return False, ["缺少相关数据"]

        if not user_allergens:
            return True, ["过敏原审查通过"]

        allergens_found = []
        drug_data = {}
        for drug in user_drugs:
            query = f"""
                    MATCH (d:`药品`)-[:成分*3]->(n:`药物`)
                    WHERE d.name = '{drug}'
                    RETURN collect(n.name) AS components
                    """
            results = self.query_database(query)
            if results:
                drug_data[drug] = set(results[0]['components'])

        for drug, components in drug_data.items():
            common_allergens = components & set(user_allergens)  # set intersection
            if common_allergens:
                allergens_found.extend([(drug, allergen) for allergen in common_allergens])

        if allergens_found:
            return False, [f"**{pair[0]}**含有过敏原**{pair[1]}**" for pair in allergens_found]
        else:
            return True, ["过敏原审查通过"]

    # 不良反应审查
    def adverse_reaction_review(self, user_drugs, disease):
        # 检查user_drugs是否为空
        if not user_drugs:
            return False, ["缺少相关数据"]

        if not disease:
            return True, ["不良反应审查通过"]

        adverse_reaction = []
        drug_data = {}
        for drug in user_drugs:
            query = f"""
                    MATCH (d:`药品`)-[:不良反应*3]->(ds:`病症`)
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
            return True, ["不良反应审查通过"]

    # 重复用药审查
    def duplicate_drug_review(self, user_drugs):
        # 检查user_drugs是否为空
        if not user_drugs:
            return False, ["缺少相关数据"]

        if len(user_drugs) == 1:
            return True, ["重复用药审查通过"]

        interactions = []
        drug_data = {}
        for drug in user_drugs:
            query = f"""
                    MATCH (d:`药品`)-[:成分*3]->(n:`药物`)
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
            return True, ["重复用药审查通过"]

    # 禁忌症审查
    def contraindication_review(self, user_drugs, disease):
        # 检查user_drugs是否为空
        if not user_drugs:
            return False, ["缺少相关数据"]

        if not disease:
            return True, ["禁忌症审查通过"]

        contraindication = []
        drug_data = {}
        for drug in user_drugs:
            query = f"""
                    MATCH (drug:`药品`)-[:用药*0..2]->()-[:患有]->(ds)
                    WHERE drug.name = '{drug}'
                    RETURN collect(ds.name) AS contraindications
                    """
            results = self.query_database(query)
            if results:
                drug_data[drug] = set(results[0]['contraindications'])

        for drug, contraindications in drug_data.items():
            common_disease = contraindications & set(disease)  # set intersection
            if common_disease:
                contraindication.extend([(drug, dis) for dis in common_disease])

        if contraindication:
            return False, [f"**{pair[0]}**有禁忌症**{pair[1]}**" for pair in contraindication]
        else:
            return True, ["禁忌症审查通过"]

    # 年龄审查
    def age_review(self, user_drugs, age):
        # 检查user_drugs是否为空
        if not user_drugs or not age:
            return False, ["缺少相关数据"]

        if not age:
            return True, ["年龄审查通过"]

        age_found = []
        for drug in user_drugs:
            query = f"""
            MATCH p1=(drug:`药品`)-[:用药*2]->(fact:`知识组`)-[:用药]->(age:`人群`),
            p2=(fact)-[:用药结果]->(useResult:`用药结果级别`) 
            WHERE drug.name = $drug AND (age.name CONTAINS '以上' or age.name CONTAINS '以下' 
            or age.name CONTAINS '大于' or age.name CONTAINS '小于' or age.name =~ '.*\\\\d+(~|至)\\\\d+.*') 
            and age.name CONTAINS '岁' 
            WITH p1,p2,age 
            RETURN 
            CASE 
            WHEN (age.name CONTAINS '以上' or age.name CONTAINS '大于') 
            and (toInteger({age}) < toInteger(apoc.text.regexGroups(age.name, '\\\\d+')[0][0])) THEN 'pass'
            WHEN (age.name CONTAINS '以下' or age.name CONTAINS '小于') 
            and (toInteger({age}) > toInteger(apoc.text.regexGroups(age.name, '\\\\d+')[0][0])) THEN 'pass' 
            END 
            AS age_pass
            """

            results = self.query_database(query, {'drug': drug})
            if results:
                age_pass = results[0]['age_pass']
                if age_pass != 'pass':
                    age_found.append((drug, age))

        if age_found:
            return False, [f"**{pair[0]}**不适宜**{pair[1]}**岁使用" for pair in age_found]
        else:
            return True, ["年龄审查通过"]

    # 特殊人群审查
    def special_population_review(self, user_drugs, population):
        # 检查user_drugs是否为空
        if not user_drugs:
            return False, ["缺少相关数据"]

        if not population:
            return True, ["特殊人群审查通过"]

        special_population = []
        drug_data = {}
        # 为每个用户提供的人群词创建一个模糊匹配的模式
        population_patterns = [f"(?i).*{pop}.*" for pop in population]  # 使用正则表达式，(?i)表示不区分大小写

        for drug in user_drugs:
            query = """
            MATCH p1=(drug:`药品`)-[:用药*2]->(fact:`知识组`)-[:用药]->(crowd:`人群`),
            p2=(fact)-[:用药结果]->(useResult:`用药结果级别`) 
            WHERE drug.name = $drug 
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
                            special_population.append((drug, pop))
        if special_population:
            return False, [f"**{pair[0]}**不适宜**{pair[1]}**使用" for pair in special_population]
        else:
            return True, ["特殊人群审查通过"]

    # 性别审查
    def gender_review(self, user_drugs, gender):
        # 检查user_drugs是否为空
        if not user_drugs:
            return False, ["缺少相关数据"]

        if not gender:
            return True, ['性别审查通过']

        gender_found = []
        drug_data = {}

        for drug in user_drugs:
            query = """
            MATCH p1=(drug:`药品`)-[:用药*2]->(fact:`知识组`)-[:用药]->(crowd:`人群`),
            p2=(fact)-[:用药结果]->(useResult:`用药结果级别`) 
            WHERE drug.name = $drug AND (crowd.name = '女性' or crowd.name = '男性')
            WITH crowd 
            RETURN
            CASE
            WHEN crowd.name = '女性' and $gender = ['男'] THEN 'pass'
            WHEN crowd.name = '男性' and $gender = ['女'] THEN 'pass'
            END
            AS gender_pass
            """

            results = self.query_database(query, {'drug': drug, 'gender': gender})
            if results:
                gender_pass = results[0]['gender_pass']
                if gender_pass != 'pass':
                    gender_found.append((drug, gender))

        if gender_found:
            return False, [f"**{pair[0]}**不适宜**{pair[1][0]}**性使用" for pair in gender_found]
        else:
            return True, ["性别审查通过"]

    # 给药途径审查
    def method_review(self, user_drugs_methods):
        # 检查user_drugs是否为空
        if not user_drugs_methods:
            return False, ["缺少相关数据"]

        method_found = []
        drug_data = {}
        for item in user_drugs_methods:
            drug = item[0]
            method = item[1]
            if not method:
                break

            query = f"""
                    MATCH (d:`药品`)-[:用药方法*3]->(a:`给药途径`)
                    WHERE d.name = '{drug}'
                    RETURN collect(a.name) AS methods
                    """
            results = self.query_database(query)
            if results:
                drug_data[drug] = set(results[0]['methods'])

        for item in user_drugs_methods:
            drug = item[0]
            methods = item[1]
            correct_methods = list(drug_data.get(drug, set()))
            chekelist = []
            for method in methods:
                if any(all(char in iter(correct_method) for char in method) for correct_method in correct_methods):
                    chekelist.append(1)
                else:
                    chekelist.append(0)
            if all(num == 0 for num in chekelist):
                method_found.append((drug, methods, correct_methods))

        # 根据检查结果返回相应的消息
        if not method_found:
            return True, ["给药途径审查通过"]
        else:
            messages = []
            for drug, methods, correct_methods in method_found:
                messages.append(f"**{drug}**给药途径**{'/'.join(methods)}**不正确，正确的给药途径为**{', '.join(correct_methods)}**")
            return False, messages

    def comprehensive_review(self, user_info):
        # user_info 是一个字典，包含了用户的年龄、性别、过敏史、疾病史、特殊人群信息和给药途径
        results = {}
        temporary_results = {}
        messages = {}
        temporary_messages = {}

        # 药物相互作用审查
        results['drug_interactions'], messages['drug_interactions'] = self.drug_interactions(
            user_info['user_drugs'])
        # 过敏审查
        results['allergy_review'], messages['allergy_review'] = self.allergy_review(
            user_info['user_drugs'], user_info['allergies'])
        # 不良反应审查
        results['adverse_reaction_review'], messages['adverse_reaction_review'] = self.adverse_reaction_review(
            user_info['user_drugs'], user_info['disease'])
        # 重复用药审查
        results['duplicate_drug_review'], messages['duplicate_drug_review'] = self.duplicate_drug_review(
            user_info['user_drugs'])
        # 禁忌症审查
        results['contraindication_review'], messages['contraindication_review'] = self.contraindication_review(
            user_info['user_drugs'], user_info['disease'])
        # 特殊人群审查
        # 合并user_info['population']和user_info['history']
        combined_list = user_info['population'] + user_info['history']
        results['special_population_review'], messages['special_population_review'] = self.special_population_review(
            user_info['user_drugs'], combined_list)
        # 性别审查
        results['gender_review'], messages['gender_review'] = self.gender_review(
            user_info['user_drugs'], user_info['gender'])
        # 给药途径审查
        results['method_review'], messages['method_review'] = self.method_review(
            user_info['user_drugs_methods'])
        # 年龄审查
        temporary_results['age_review_1'], temporary_messages['age_review_1'] = self.age_review(
            user_info['user_drugs'], user_info['age'])
        temporary_results['age_review_2'], temporary_messages['age_review_2'] = self.special_population_review(
            user_info['user_drugs'], user_info['age_group'])
        # results['age_review'], messages['age_review'] =
        age_review_1 = temporary_results['age_review_1']
        age_review_2 = temporary_results['age_review_2']
        # 设置results['age_review']的值
        results['age_review'] = age_review_1 and age_review_2
        # 初始化messages['age_review']
        messages['age_review'] = []
        # 如果age_review_1为假，则添加messages['age_review_1']的内容
        if not age_review_1:
            messages['age_review'] += temporary_messages['age_review_1']
        # 如果age_review_2为假，则添加messages['age_review_2']的内容
        if not age_review_2:
            messages['age_review'] += temporary_messages['age_review_2']

        if age_review_1 and age_review_2:
            messages['age_review'].append("年龄审查通过")

        # 综合所有结果和消息
        comprehensive_result = all(result for result in results.values())
        # comprehensive_message = "Comprehensive Review Results:\n" + "\n".join(
        #     f"{key}: {msg}" for key, msg in messages.items() if msg)
        # 构建一个新的字典，仅包含有消息的审查项
        comprehensive_message = {key: msg for key, msg in messages.items() if msg}
        return comprehensive_result, comprehensive_message


if __name__ == '__main__':
    uri = "bolt://localhost:7687"
    user = "neo4j" # Your user name, default name is neo4j
    password = "neo4j" # Your password, default password is neo4j
    system = DrugReviewSystem(uri, user, password)
    user_drugs = ["氯雷他定片", "氨茶碱缓释片", "氧氟沙星氯化钠注射液", "丙硫异烟胺肠溶片", '二仙丸', '来氟米特片']
    allergies = ["氯雷他定", "头孢"]
    disease = ["感冒", "头痛", "咳嗽", "恶心"]
    # population = ["哺乳期", "老年人"]
    population = []
    user_drugs_methods = [["氧氟沙星氯化钠注射液", ["口服", "冲服"]], ["氧氟沙星氯化钠注射液", ["静脉缓慢滴注"]]]
    age = 10
    gender = ['男']
    user_info = {
        'user_drugs': user_drugs,
        'allergies': allergies,
        'disease': disease,
        'population': population,
        'user_drugs_methods': user_drugs_methods,
        'age': age,
        'gender': gender,
        'history': [],
        "age_group": ["儿童"]
    }
    result, message = system.comprehensive_review(user_info)
    print(message)



