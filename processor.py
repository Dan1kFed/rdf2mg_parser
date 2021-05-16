import copy
# import matplotlib.pyplot as plt
import markov_clustering as mc
import networkx as nx


class JSONParser:
    @staticmethod
    def _get_metavertices_(cluster_list: list, verts_list: list) -> list:
        """Это функция для создания листа с метавершинами"""
        vert_list = []
        verts_done = []
        for cl in range(len(cluster_list)):
            metavert_dict = {'name':cluster_list[cl]['cluster'],
                             'parent':'None'}
            for vert in cluster_list[cl]['vertices']:
                vert_dict = {'name':vert,
                             'parent':metavert_dict['name']}
                vert_list.append(vert_dict)
                verts_done.append(vert)
            vert_list.append(metavert_dict)
        verts_done = list(set(verts_done))
        for vert in verts_done:
            verts_list.remove(vert)
        for vert in verts_list:
            vert_dict = {'name':vert,
                         'parent':'None'}
            vert_list.append(vert_dict)
        return vert_list

    @staticmethod
    def download_to_JSON(ttlfile, ban_list, attr_list, oriented: bool) -> dict:
        """TODO: сделать более универсальным"""
        ban_list = ban_list.replace("'", "")
        ban_list = ban_list.split(', ')
        attr_list = attr_list.replace("'", "")
        attr_list = attr_list.split(', ')
        bigraph_list = []
        lines_in_file = ttlfile.read().decode('utf-8')
        lines_in_file = lines_in_file.split('\n')
        for line in lines_in_file:
            bigraph_dict = {}
            if line.startswith('w') and not any(map(lambda w:w in line, ban_list)) \
                    and not any(map(lambda w:w in line, attr_list)):
                splited_line = line.split(' ')
                bigraph_dict['subject'] = splited_line[0]
                bigraph_dict['predicate'] = splited_line[1]
                bigraph_dict['object'] = splited_line[2]
                bigraph_list.append(bigraph_dict)
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
    @staticmethod
    def rdf2mg(in_json: dict):
        """Метод для кластеризации в ширину
        [{cluster: name,
           vertices: [vert1, vert2]}]"""
        cluster_list = []
        bigraph_list = copy.deepcopy(in_json['bigraph'])
        vert_list = list(set(bigraph_list[dic]['subject'] for dic in range(len(bigraph_list))))
        for vert in vert_list:
            subj_list = list(filter(lambda subj: subj['subject'] == vert, bigraph_list))
            pred_list = list(set(subj_list[dic]['predicate'] for dic in range(len(subj_list))))
            for pred in pred_list:
                vertices = list(filter(lambda predicate: predicate['predicate'] == pred, subj_list))
                if len(vertices) > 1:
                    cluster_dict = {'cluster': pred,
                                    'vertices': list(set(vertices[dic]['object']for dic in range(len(vertices))))}
                    cluster_list.append(cluster_dict)
        return cluster_list




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
