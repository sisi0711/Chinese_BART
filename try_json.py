from stanfordcorenlp import StanfordCoreNLP

def index():
    sentence_get = "这是一个例子"
    nlp = StanfordCoreNLP('http://202.112.194.61', port=8085, lang='zh')
    # 句法分析
    sen_pos_tag = nlp.pos_tag('我喜欢吃苹果。')
    # 结果：[('我', 'PN'), ('喜欢', 'VV'), ('吃', 'VV'), ('苹果', 'NN'), ('。', 'PU')]
    sen_dep = nlp.dependency_parse('我喜欢吃苹果。')
    sen_dep_sort = sorted(sen_dep, key=lambda x: x[2])
    # 结果：[('nsubj', 2, 1), ('ROOT', 0, 2), ('ccomp', 2, 3), ('dobj', 3, 4), ('punct', 2, 5)]

    parser_string = ""
    '''
    1	我	_	PN	PN	_	2	nsubj	_	_
    2	喜欢	_	VV	VV	_	0	root	_	_
    3	吃	_	VV	VV	_	2	ccomp	_	_
    4	苹果	_	NN	NN	_	3	dobj	_	_

    '''
    for i in range(0,len(sen_dep)):
        line = str(i + 1) + "\t" + sen_pos_tag[i][0] + "\t_\t" + sen_pos_tag[i][1] + "\t" + sen_pos_tag[i][1] + "\t_\t" + str(sen_dep_sort[i][1]) + "\t" + sen_dep_sort[i][0] + "\t_\t_\n"
        parser_string += line
    print(parser_string)
    # parser_string = parser_string.encode('utf-8')
    word = ['ROOT']
    for i in range(0, len(sen_pos_tag)):
        word.append(sen_pos_tag[i][0])

    # 转为json文件
    dependencies = []
    tokens = []
    len_now = 0
    string_now = parser_string
    for i in range(1, len(word)):
        index_now = string_now.index('\n')
        tab_num = 0
        tab_loc = []
        for j in range(0, index_now):
            if string_now[j] == '\t':
                tab_loc.append(j)
                tab_num = tab_num + 1
         # 完成dependencies的构建
        dep_tmp = {}
        dep_tmp['dep'] = string_now[tab_loc[6] + 1:tab_loc[7]]
        dep_tmp['governor'] = int(string_now[tab_loc[5] + 1:tab_loc[6]])
        dep_tmp['governorGloss'] = word[dep_tmp['governor']]
        dep_tmp['dependent'] = i
        dep_tmp['dependentGloss'] = word[i]
        # print dep_tmp
        if dep_tmp['governor'] == 0:
            dependencies.insert(0, dep_tmp)
        else:
            dependencies.append(dep_tmp)
        # 完成tokens的构建
        token_tmp = {}
        token_tmp['index'] = i
        token_tmp['word'] = word[i]
        token_tmp['originalText'] = ""
        token_tmp['characterOffsetBegin'] = len_now
        token_tmp['characterOffsetEnd'] = len_now + len(word[i])
        token_tmp['pos'] = string_now[tab_loc[2] + 1:tab_loc[3]]
        tokens.append(token_tmp)
        # 转移
        len_now = len_now + len(word[i])
        string_now = string_now[index_now + 1:]
    sentence = {}
    sentence['index'] = 0
    sentence['basicDependencies'] = dependencies
    sentence['tokens'] = tokens
    sentences = [sentence]
    data = {'sentences': sentences, 'Conll_data': parser_string, 'sentence_get': sentence_get}
    print(data)

if __name__ == "__main__":
    index()