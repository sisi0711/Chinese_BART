import spacy
import pybart.api 
from spacy_conll import ConllFormatter

# Load a UD-based english model
nlp = spacy.load("en_ud_model_sm") # here you can change it to md/sm/lg as you preffer

# Add BART converter to spaCy's pipeline

nlp.add_pipe("pybart_spacy_pipe", last="True", config={'remove_extra_info':True}) # you can pass an empty config for default behavior, this is just an example

# Test the new converter component
doc = nlp("He saw me while driving")
for sent_graph in doc._.parent_graphs_per_sent:
   for edge in sent_graph.edges:
       print([doc[t.i].text for t in edge.head.tokens], f" --{edge.label_}-> ", [doc[t.i].text for t in edge.tail.tokens])

# Output:
# ['saw'] --root-> ['saw']
# ['saw'] --nsubj-> ['He']
# ['saw'] --dobj-> ['me']
# ['saw'] --advcl:while-> ['driving']
# ['driving'] --mark-> ['while']
# ['driving'] --nsubj-> ['He']