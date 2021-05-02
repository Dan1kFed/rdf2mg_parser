from bg_model import Subject, Predicate, BGraph, psql_db
from mg_model import Vertex, Edge, Relations, psql_db_mg
import copy
import matplotlib.pyplot as plt
import markov_clustering as mc
import networkx as nx

ban_list = ['rdf', 'rdfs', 'dbo']
attr_list = ['oa:hasTarget', 'xsd:dateTime']


class JSONParser:
    @staticmethod
    def _get_metavertices_(cluster_list: list, verts_list: list) -> list:
        """Это функция для создания листа с метавершинами"""
        vert_list = []
        for cl in range(len(cluster_list)):
            metavert_dict = {'name':cluster_list[cl]['cluster'],
                             'parent':'None'}
            for vert in cluster_list[cl]['vertices']:
                vert_dict = {'name':vert,
                             'parent':metavert_dict['name']}
                vert_list.append(vert_dict)
                verts_list.remove(vert)
            vert_list.append(metavert_dict)
        for vert in verts_list:
            vert_dict = {'name':vert,
                         'parent':'None'}
            vert_list.append(vert_dict)
        return vert_list

    @staticmethod
    def download_to_JSON(ttlfile, ban_list: list, attr_list: list, oriented: bool) -> dict:
        """TODO: сделать более универсальным"""
        bigraph_list = []
        lines_in_file = ttlfile.read().decode('utf-8')
        lines_in_file = lines_in_file.split('\n')
        print(lines_in_file[:20])
        for line in lines_in_file:
            bigraph_dict = {}
            if line.startswith('w') and not any(map(lambda w:w in line, ban_list)) \
                    and not any(map(lambda w:w in line, attr_list)):
                splited_line = line.split(' ')
                bigraph_dict['subject'] = splited_line[0]
                bigraph_dict['predicate'] = splited_line[1]
                bigraph_dict['object'] = splited_line[2]
                bigraph_list.append(bigraph_dict)
            else:
                pass
        inJSON_dict = {}
        inJSON_dict['oriented'] = oriented
        inJSON_dict['attributes'] = attr_list
        inJSON_dict['bigraph'] = bigraph_list
        inJSON_dict['ban_list'] = ban_list
        return inJSON_dict

    @staticmethod
    def output_to_JSON(cluster, inJSON: dict) -> dict:
        edge_list = []
        bigraph_list = copy.deepcopy(inJSON['bigraph'])
        print(inJSON['bigraph'][2])
        bigraph_list_pop = [val.pop('predicate') for val in bigraph_list]
        vert_list = list(set(val for dic in bigraph_list for val in dic.values()))
        bigraph_list = copy.deepcopy(inJSON['bigraph'])
        for edge in bigraph_list:
            edge_dict = {'name': edge['predicate'],
                         'source': edge['subject'],
                         'direction': edge['object']}
            edge_list.append(edge_dict)
        vertful_list = JSONParser._get_metavertices_(cluster_list = cluster, verts_list = vert_list)
        outJSON_dict = {}
        outJSON_dict['oriented'] = inJSON['oriented']
        outJSON_dict['vertices'] = vertful_list
        outJSON_dict['attributes'] = inJSON['attributes']
        outJSON_dict['edges'] = edge_list
        return outJSON_dict


class WidthCluster:
    def __bg2mg__(self, subject, pc_list):
        """TODO: удолить???"""
        """Все записи из bggraph у которых предикат == [3, 7] пишем в атрибуты
         vertex, создаем vertex по каждому subject, делаем get_or_none обжекта
         из таблицы bggrapg, если get то делаем связь двух vertex, если none
         то создаем новую vertex и делаем с ней связь.
         Добавляем метавершины согласно анализу в pc_list"""
        vert_from = Vertex.get_or_none(Vertex.name == subject)
        if vert_from is None:
            vert_from = Vertex(name = subject)
            vert_from.save()
        for pred in pc_list:
            if not pred['metavertex'] in attr_list:
                for vert in pred['vertices']:  # создаем верщины из pc_list
                    vert_to = Vertex.get_or_none(Vertex.name == vert)
                    if vert_to is None:
                        vert_to = Vertex(name = vert)
                        vert_to.save()
                    edge_name = list(Predicate.select().where(Predicate.id == pred['metavertex']).dicts())
                    Edge.create(name = edge_name[0]['name'],
                                from_vertex_id = vert_from.id,
                                to_vertex_id = vert_to.id)
                if len(pred['vertices']) > 1:
                    mv_name = list(Predicate.select().where(Predicate.id == pred['metavertex']).dicts())
                    metavert = Vertex(name = mv_name[0]['name'])
                    metavert.save()
                    pred['vertices'].append(vert_from.name)
                    for v in pred['vertices']:
                        low_vert = Vertex.get(Vertex.name == v)
                        Relations.create(name = mv_name[0]['name'],
                                         higher_vertex_id = metavert.id,
                                         lower_vertex_id = low_vert)
            else:
                attr_name = list(Predicate.select().where(Predicate.id == pred['metavertex']).dicts())
                vert_from.attribute_prefix = attr_name[0]['name']
                vert_from.save()
                vert_from.attribute_value = pred['vertices'][0]
                vert_from.save()

    @staticmethod
    def rdf2mg(rdffile):
        """TODO: переписать для обработки дикта"""
        """1) Делаем rdf2bg. (пока можно закоментить, чтобы время сэкономить)
        2) Делаем анализ таблицы bggraph: если predicate не 3 и не 7, то для каждого
        subject составляем ранжирование наиболее частых predicate в виде дикта:
        {predicate_name: кол-во встречающихся}; и думаем можно ли выделить из этого метавершину,
        если да то пишем отношение в pc_list: [{metavertex_name: [list_of_vertices]}]
        3) Делаем bg2mg"""
        # self.__rdf2bg__('ru_0_rdf_result.ttl')
        sub_lenght = len(list(Subject.select()))
        for subj in range(2):  # test
            pc_list = []
            subj_name = list(Subject.select(Subject.name).where(Subject.id == subj).dicts())
            trip = list(BGraph.select().where(BGraph.subject_id == subj).dicts())
            if trip:
                print(trip)
                preds = set([pred['predicate_id'] for pred in trip])  # уникальные предикаты
                print(preds)
                for pred in preds:
                    mv_dict = {}
                    names = BGraph.select(BGraph.object_name).where(BGraph.subject_id == subj,
                                                                    BGraph.predicate_id == pred).dicts()
                    vertices = [vert['object_name'] for vert in names]
                    mv_dict['metavertex'] = pred
                    mv_dict['vertices'] = vertices
                    pc_list.append(mv_dict)
                print(pc_list)
                # self.__bg2mg__(subj_name[0]['name'], pc_list)


class LengthCluster:
    @staticmethod
    def make_graph_from_JSONin(JSONin):
        g = nx.Graph()
        bigraph_length = len(JSONin['bigraph'])
        bigraph_list = copy.deepcopy(JSONin['bigraph'])
        bigraph_list_pop = [val.pop('predicate') for val in bigraph_list]
        vert_list = list(set(val for dic in bigraph_list for val in dic.values()))
        for vert in vert_list:
            g.add_node(vert)
        for edge in range(bigraph_length):
            g.add_edge(bigraph_list[edge]['subject'], bigraph_list[edge]['object'])
        return g

    @staticmethod
    def cluster_transform(cluster_list, nx_graph):
        """Метод для трансофрмации исходного графа и кластеров из маркова к виду:
         [{cluster: name,
           vertices: [vert1, vert2]}]"""
        transformed_clusters = []
        original_verts = list(nx_graph.nodes)
        cluster_list = [tup for tup in cluster_list if len(tup) >= 2]
        for i in range(len(cluster_list)):
            transformed_cluster_dict = {}
            transformed_cluster_vert_list = []
            transformed_cluster_dict['cluster'] = i
            for vert in range(len(cluster_list[i])):
                transformed_cluster_vert_list.append(original_verts[cluster_list[i][vert]])
            transformed_cluster_dict['vertices'] = transformed_cluster_vert_list
            transformed_clusters.append(transformed_cluster_dict)
        return transformed_clusters

    @staticmethod
    def markov_clustering(JSONin):
        nx_graph = LengthCluster.make_graph_from_JSONin(JSONin)
        matrix = nx.to_scipy_sparse_matrix(nx_graph)
        print('clustreing...')
        result = mc.run_mcl(matrix)  # run MCL with default parameters
        clusters = mc.get_clusters(result)
        transformed_clusters = LengthCluster.cluster_transform(cluster_list = clusters, nx_graph = nx_graph)
        # print(clusters)
        # print('drawing...')
        # plt.rcParams["figure.figsize"] = (40, 40)
        # mc.draw_graph(matrix, clusters)
        return transformed_clusters
