from bg_model import Subject, Predicate, BGraph, psql_db

ban_list = ['rdf', 'rdfs', 'dbo']


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


def bg2mg(bgraph, pc_dict):
    """Все записи из bggraph у которых предикат == [3, 7] пишем в атрибуты
     vertex, создаем vertex по каждому subject, делаем get_or_none обжекта
     из таблицы bggrapg, если get то делаем связь двух vertex, если none
     то создаем новую vertex и делаем с ней связь.
     Добавляем метавершины согласно анализу в pc_dict"""
    pass


def rdf2mg(rdffile):
    """1) Делаем rdf2bg. (пока можно закоментить, чтобы время сэкономить)
    2) Делаем анализ таблицы bggraph: если predicate не 3 и не 7, то для каждого
    subject составляем ранжирование наиболее частых predicate в виде дикта:
    {predicate_name: кол-во встречающихся}; и думаем можно ли выделить из этого метавершину,
    если да то пише отношение в pc_dict: {metavertex_name: [list_of_vertices]}
    3) Делаем bg2mg"""
    pass


psql_db.drop_tables([Subject, Predicate, BGraph])
psql_db.create_tables([Subject, Predicate, BGraph])
rdf2bg('ru_0_rdf_result.ttl')
