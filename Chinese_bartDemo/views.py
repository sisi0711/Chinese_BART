from pybart.pybart.api import convert_bart_conllu
from django.http import HttpResponse
from django.shortcuts import render, redirect
import json
from stanfordcorenlp import StanfordCoreNLP
#以下两行的作用是让结果唯一：
from langdetect import DetectorFactory
DetectorFactory.seed = 0

def parser_build_json(string, word, dependencies, tokens):
    '''
    1       我      _       PN      PN      _       3       conj    _       _
    2       和      _       CC      CC      _       3       cc      _       _
    3       妈妈    _       NN      NN      _       5       nsubj   _       _
    4       正在    _       AD      AD      _       5       advmod  _       _
    5       做饭    _       VV      VV      _       0       ROOT    _       _
    6       。      _       PU      PU      _       5       punct   _       _
    '''
    len_now = 0
    string_now = string
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


def bart_build_json(string, word, dependencies, tokens):
    '''
    1       我      _       PN      PN      _       3       conj    3:conj_和|5:nsubj       _
    2       和      _       CC      CC      _       3       cc      3:cc    _
    3       妈妈    _       NN      NN      _       5       nsubj   5:nsubj _
    4       正在    _       AD      AD      _       5       advmod  5:advmod        _
    5       做饭    _       VV      VV      _       0       ROOT    0:ROOT  _
    6       。      _       PU      PU      _       5       punct   5:punct _
    '''
    len_now = 0
    string_now = string
    for i in range(1, len(word)):
        index_now = string_now.index('\n')
        tab_num = 0
        tab_loc = []
        for j in range(0, index_now):
            if string_now[j] == '\t':
                tab_loc.append(j)
                tab_num = tab_num + 1
         # 完成dependencies的构建
        #多依赖
        deps = string_now[tab_loc[7] + 1:tab_loc[8]].split("|")
        if len(deps) == 1:
            dep_tmp = {}
            temp = deps[0].split(":")
            dep_tmp['dep'] = "".join(temp[1:])
            dep_tmp['governor'] = int(temp[0])
            dep_tmp['governorGloss'] = word[dep_tmp['governor']]
            dep_tmp['dependent'] = i
            dep_tmp['dependentGloss'] = word[i]
            if dep_tmp['governor'] == 0:
                dependencies.insert(0, dep_tmp)
            else:
                dependencies.append(dep_tmp)
        else:
            for dep in deps:
                dep_tmp = {}
                temp = dep.split(":")
                dep_tmp['dep'] = "".join(temp[1:])
                dep_tmp['governor'] = int(temp[0])
                dep_tmp['governorGloss'] = word[dep_tmp['governor']]
                dep_tmp['dependent'] = i
                dep_tmp['dependentGloss'] = word[i]
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


def change_bart_string(string):
    '''
    1       我      _       PN      PN      _       3       conj    3:conj_和|5:nsubj       _
    2       和      _       CC      CC      _       3       cc      3:cc    _
    3       妈妈    _       NN      NN      _       5       nsubj   5:nsubj _
    4       正在    _       AD      AD      _       5       advmod  5:advmod        _
    5       做饭    _       VV      VV      _       0       ROOT    0:ROOT  _
    6       。      _       PU      PU      _       5       punct   5:punct _
    '''
    sentence = string.split("\n")
    new_string = ""
    i = 1
    j = 0
    print(sentence)
    for line in sentence:
        parts = line.split()
        if len(parts) == 8:
            new_id, upos, xpos, feats, head, deprel, deps, misc = parts[:8]
            form = " "
            lemma = " "
        elif len(parts) == 10:
            new_id, form, lemma, upos, xpos, feats, head, deprel, deps, misc = parts[:10]
        else:
            continue

        new_deps = deps.split("|")
        print(new_deps)
        if len(new_deps) == 1:
            temp = new_deps[0].split(":")
            h = int(temp[0])
            new_line = str(i) + "\t" + form + "\t" + lemma + "\t" + upos + "\t" + xpos + "\t" + feats + "\t" + str(j + int(temp[0])) + "\t" + temp[1] + "\t_\t_\n"
            new_string += new_line
            i += 1
        else:
            for new_dep in new_deps:
                temp = new_dep.split(":")
                new_line = str(i) + "\t" + form + "\t" + lemma + "\t" + upos + "\t" + xpos + "\t" + feats + "\t" + str(j + int(temp[0])) + "\t" + temp[1] + "\t_\t_\n"
                new_string += new_line
                i += 1
                j += 1
    print(new_string)
    return new_string


def index(sentence_get):
    nlp = StanfordCoreNLP('http://202.112.194.61', port=8085, lang='zh')
    # 句法分析
    sen_pos_tag = nlp.pos_tag(sentence_get)
    # 结果：[('我', 'PN'), ('喜欢', 'VV'), ('吃', 'VV'), ('苹果', 'NN'), ('。', 'PU')]
    sen_dep = nlp.dependency_parse(sentence_get)
    sen_dep_sort = sorted(sen_dep, key=lambda x: x[2])
    # 结果：[('nsubj', 2, 1), ('ROOT', 0, 2), ('ccomp', 2, 3), ('dobj', 3, 4), ('punct', 2, 5)]

    parser_string = ""

    for i in range(0,len(sen_dep)):
        line = str(i + 1) + "\t" + sen_pos_tag[i][0] + "\t_\t" + sen_pos_tag[i][1] + "\t" + sen_pos_tag[i][1] + "\t_\t" + str(sen_dep_sort[i][1]) + "\t" + sen_dep_sort[i][0] + "\t_\t_\n"
        parser_string += line
    word = ['ROOT']
    for i in range(0, len(sen_pos_tag)):
        word.append(sen_pos_tag[i][0])

    # 基本句法依存
    dependencies = []
    tokens = []
    parser_build_json(parser_string, word, dependencies, tokens)
    sentence = {}
    sentence['index'] = 0
    sentence['basicDependencies'] = dependencies
    sentence['tokens'] = tokens
    sentences = [sentence]
    data1 = {'sentences': sentences, 'Conll_data': parser_string, 'sentence_get': sentence_get}

    #加强依存
    bart_string = convert_bart_conllu(parser_string)
    dependencies_un = []
    tokens_un = []
    bart_build_json(bart_string, word, dependencies_un, tokens_un)
    sentence_un = {}
    sentence_un['index'] = 0
    sentence_un['basicDependencies'] = dependencies_un
    sentence_un['tokens'] = tokens_un
    sentences_un = [sentence_un]

    data2 = {'sentences': sentences_un, 'Conll_data': bart_string, 'sentence_get': sentence_get}
    data = {'data1': data1, 'data2': data2}
    # print(data['data2'])
    return data


def demo(request):
    if request.method == 'POST':
        post_data = json.loads(request.body)
        query = post_data.get("query")
        json_data = json.dumps(index(query))
        # print(json_data)
        return HttpResponse(json_data, content_type="application/json")
    else:
        return render(request, 'demo.html')