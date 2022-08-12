# WED

#### 使用方法

```python
from WED.api import convert_bart_conllu
converted = convert_bart_conllu(your_sentences)
print(converted)
# 如果您需要输出到文件
with open('result.conll', "w", encoding = "utf-8") as f:
    f.write(converted)
```

#### 输出

第1列为序号，第2列为词语内容，第4、5列为该词语的词性标签，第7列为该词语的head，第8列为由head指向该词语的依存弧上的依存标签，第9列为增强后的依存弧及其标签。

```
1    我    _    PN    PN    _    3    conj    3:conj_和|5:nsubj    _
2    和    _    CC    CC    _    3    cc    3:cc    _
3    妈妈    _    NN    NN    _    5    nsubj    5:nsubj    _
4    正在    _    AD    AD    _    5    advmod    5:advmod    _
5    做饭    _    VV    VV    _    0    ROOT    0:ROOT    _
6    。    _    PU    PU    _    5    punct    5:punct    _
```

