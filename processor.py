from bg_model import Subject, Predicate, BGraph, psql_db
from mg_model import Vertex, Edge, Relations, psql_db_mg

ban_list = ['rdf', 'rdfs', 'dbo']
attr_list = [3, 7]


def rdf2bg(rdffile):
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


def bg2mg(subject, pc_list):
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
            for vert in pred['vertices']:
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


def rdf2mg(rdffile):
    """1) Делаем rdf2bg. (пока можно закоментить, чтобы время сэкономить)
    2) Делаем анализ таблицы bggraph: если predicate не 3 и не 7, то для каждого
    subject составляем ранжирование наиболее частых predicate в виде дикта:
    {predicate_name: кол-во встречающихся}; и думаем можно ли выделить из этого метавершину,
    если да то пише отношение в pc_list: [{metavertex_name: [list_of_vertices]}]
    3) Делаем bg2mg"""
    # rdf2bg('ru_0_rdf_result.ttl')
    sub_lenght = len(list(Subject.select()))
    for subj in range(11):
        pc_list = []
        trip = list(BGraph.select().where(BGraph.subject_id == subj).dicts())
        subj_name = list(Subject.select(Subject.name).where(Subject.id == subj).dicts())
        if trip:
            preds = set([pred['predicate_id'] for pred in trip])
            for pred in preds:
                mv_dict = {}
                names = BGraph.select(BGraph.object_name).where(BGraph.subject_id == subj,
                                                                BGraph.predicate_id == pred).dicts()
                vertices = [vert['object_name'] for vert in names]
                mv_dict['metavertex'] = pred
                mv_dict['vertices'] = vertices
                pc_list.append(mv_dict)
            bg2mg(subj_name[0]['name'], pc_list)


"""НЕ ТРОГАЙ, СНАЧАЛА ПОДУМАЙ"""
psql_db_mg.drop_tables([Vertex, Edge, Relations])
psql_db_mg.create_tables([Vertex, Edge, Relations])
rdf2mg('aaa')
# print('hui')
# psql_db.drop_tables([Subject, Predicate, BGraph])
# psql_db.create_tables([Subject, Predicate, BGraph])
# rdf2bg('ru_0_rdf_result.ttl')
