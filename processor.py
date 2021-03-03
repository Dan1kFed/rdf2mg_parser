from bg_model import Subject, Predicate, BGraph, psql_db
from mg_model import Vertex, Edge, Relations, psql_db_mg
import matplotlib.pyplot as plt
import markov_clustering as mc
import networkx as nx

ban_list = ['rdf', 'rdfs', 'dbo']
attr_list = [3, 7]


class JSONParser:
    pass


class WidthCluster:
    def __rdf2bg__(self, rdffile):
        rdf_list = []
        for line in open(rdffile, 'r').readlines():
            rdf_dict = {}
            if line.startswith('w') and not any(map(lambda w: w in line, ban_list)):
                splited_line = line.split(' ')
                rdf_dict['subject'] = splited_line[0]
                rdf_dict['predicate'] = splited_line[1]
                rdf_dict['object'] = splited_line[2]
                rdf_list.append(rdf_dict)
        uniq_subj = sorted(list(set(dic['subject'] for dic in rdf_list)))
        uniq_pred = sorted(list(set(dic['predicate'] for dic in rdf_list)))
        for subj in uniq_subj:
            Subject.create(name = subj)
        for pred in uniq_pred:
            Predicate.create(name = pred)
        for trip in rdf_list:
            subj = Subject.get(Subject.name == trip['subject'])
            pred = Predicate.get(Predicate.name == trip['predicate'])
            BGraph.create(subject_id = subj.id,
                          predicate_id = pred.id,
                          object_name = trip['object'])

    def __bg2mg__(self, subject, pc_list):
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
    def make_graph_from_pg():
        g = nx.Graph()
        sub_lenght = len(list(Subject.select()))
        vert_list = list(Subject.select().dicts())
        for i in range(1000):
            g.add_node(vert_list[i]['name'])
        for subj in range(1000):
            subj_name = list(Subject.select(Subject.name).where(Subject.id == subj).dicts())
            trip = list(BGraph.select().where(BGraph.subject_id == subj).dicts())
            if trip:
                preds = set([pred['predicate_id'] for pred in trip])  # уникальные предикаты
                for pred in preds:
                    names = BGraph.select(BGraph.object_name).where(BGraph.subject_id == subj,
                                                                    BGraph.predicate_id == pred).dicts()
                    vert_to_list = [vert['object_name'] for vert in names]
                    for v in vert_to_list:
                        g.add_edge(subj_name[0]['name'], v)
        return g

    @staticmethod
    def markov_clustering(nx_graph):
        matrix = nx.to_scipy_sparse_matrix(nx_graph)
        print('clustreing...')
        result = mc.run_mcl(matrix)  # run MCL with default parameters
        clusters = mc.get_clusters(result)
        print('drawing...')
        plt.rcParams["figure.figsize"] = (40, 40)
        mc.draw_graph(matrix, clusters)


print('ffff')
"""НЕ ТРОГАЙ, СНАЧАЛА ПОДУМАЙ"""
# psql_db_mg.drop_tables([Vertex, Edge, Relations])
# psql_db_mg.create_tables([Vertex, Edge, Relations])
# WidthCluster.rdf2mg('aaa')
a = LengthCluster.make_graph_from_pg()
LengthCluster.markov_clustering(a)
# print('hui')
# psql_db.drop_tables([Subject, Predicate, BGraph])
# psql_db.create_tables([Subject, Predicate, BGraph])
# rdf2bg('ru_0_rdf_result.ttl')
