from pybart.api import convert_bart_conllu

# read a CoNLL-U formatted file
with open('UD_data/UD.conll','r', encoding = "utf-8") as f:
  sents = f.read()

# convert
converted = convert_bart_conllu(sents)

print(converted)
# use it, probably wanting to write the textual output to a new file
# with open('chinese_data/bart.dev.ctb51.ud.conllu', "w", encoding = "utf-8") as f:
#     f.write(converted)