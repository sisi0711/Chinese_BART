from stanfordcorenlp import StanfordCoreNLP

#如果要用其他语言，需要单独设置
nlp = StanfordCoreNLP('http://202.112.194.61', port=8085, lang='zh')
#nlp = StanfordCoreNLP('http://127.0.0.1', port=9000, lang='zh')

print(nlp.pos_tag('我喜欢吃苹果。'))
#结果：[('这', 'PN'), ('是', 'VC'), ('一', 'CD'), ('个', 'M'), ('例子', 'NN'), ('。', 'PU')]

parser = nlp.dependency_parse('我喜欢吃苹果。')
print(sorted(parser, key=lambda x: x[2]))
#结果：[('ROOT', 0, 5), ('nsubj', 5, 1), ('cop', 5, 2), ('nummod', 5, 3), ('mark:clf', 3, 4), ('punct', 5, 6)]

