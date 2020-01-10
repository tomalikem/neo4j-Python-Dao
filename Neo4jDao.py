import Resources
import re
import copy


class Neo4jDao:
    def __init__(self):
        self.driver = Resources.driver

    def create_node(self, obj):
        label = obj.__class__.__name__
        properties = obj.__dict__
        query = "CREATE (x:" + label + "{" + self.__parse_dict(properties) + "}) RETURN x.id"
        with self.driver.session() as session:
            return session.run(query)

    def get_one_by_attr(self, empty_object, class_name, attr, val):
        if self.__unsafe(class_name, attr, val):
            raise ValueError("Special characters detected")
        query = "MATCH (x:" + class_name + "{" + attr + ":'" + val + "'}) RETURN x"
        with self.driver.session() as session:
            node = session.run(query).single().values()[0]
        empty_object.id = node.id
        for (x, y) in node.items():
            empty_object.__dict__[x] = y
        return empty_object

    def get_all_by_attr(self, empty_object, class_name, attr, val):
        if self.__unsafe(class_name, attr, val):
            raise ValueError("Special characters detected")
        query = "MATCH (x:" + class_name + "{" + attr + ":'" + val + "'}) RETURN x"
        with self.driver.session() as session:
            records = session.run(query).records()
        return self.__parse_records_to_nodes(empty_object, records)

    def create_relation(self, obj_from, obj_to, rel_type, dict_of_attr):
        query = " MATCH (x),(y)" + \
                " WHERE ID(x)=" + str(obj_from.id) + " AND " + "ID(y)=" + str(obj_to.id) + \
                " CREATE(x)-[r:" + rel_type + "{" + self.__parse_dict(dict_of_attr) + "}]->(y)" + \
                " RETURN r"
        with self.driver.session() as session:
            return session.run(query).single().values()[0]

    def get_related_nodes(self, node_from, rel_type, empty_object):
        query = " MATCH(x)-[r:" + rel_type + "]->(y) WHERE ID(x) = " + str(node_from.id) + " RETURN y"
        with self.driver.session() as session:
            records = session.run(query).records()
        return self.__parse_records_to_nodes(empty_object, records)

    @staticmethod
    def __parse_dict(properties):
        parsed_string = ""
        first = True
        for key in properties.keys():
            if Neo4jDao.__unsafe(key, properties[key]):
                raise ValueError("Special characters detected")
            if first:
                first = False
            else:
                parsed_string = parsed_string + ","
            parsed_string = parsed_string + key + ":\"" + properties[key] + "\""
        return parsed_string

    @staticmethod
    def __unsafe(*args):
        pattern = re.compile("^[a-zA-Z0-9:\-]+$")
        for arg in args:
            if not pattern.match(str(arg)):
                print(arg)
                return True

    @staticmethod
    def __parse_records_to_nodes(empty_object, records):
        result_list = []
        for record in records:
            node = record.values()[0]
            obj = copy.copy(empty_object)
            obj.id = node.id
            for (x, y) in node.items():
                obj.__dict__[x] = y
            result_list.append(obj)
        return result_list


