
def parse_conllu(text):
    # for each sentence
    for sent in text.strip().split('\n\n'):
        lines = sent.strip().split('\n')
        if not lines:
            continue
        comments = []

        for line in lines:
            if line.startswith('#'):
                comments.append(line)
                continue

            parts = line.split()

            if len(parts) > 10:
                parts = line.split("\t")
                if len(parts) > 10:
                    raise ValueError("text must be a basic CoNLL-U format, received too many columns or separators.")

            if len(parts) == 8:
                new_id, upos, xpos, feats, head, deprel, deps, misc = parts[:8]
                form = " "
                lemma = " "
            elif len(parts) == 10:
                new_id, form, lemma, upos, xpos, feats, head, deprel, deps, misc = parts[:10]

            check = head + ":" + deprel
            results = deps.split("|")
            if check in results:
                results.remove(check)
                r_len = len(results)
                if r_len == 0:
                    deps = "_"
                else:
                    temp = results[0]
                    for i in range(1, r_len):
                        temp = temp + "|" + results[i]
                    deps = temp
            if new_id != "1":
                sen = new_id + "\t" + form + "\t" + lemma + "\t" + upos + "\t" + xpos + "\t" + feats + "\t" + head + "\t" + deprel + "\t" + deps + "\t" + misc + "\n"
            else:
                sen = "\n" + new_id + "\t" + form + "\t" + lemma + "\t" + upos + "\t" + xpos + "\t" + feats + "\t" + head + "\t" + deprel + "\t" + deps + "\t" + misc + "\n"

            with open('chinese_data/check.bart.train.ctb51.ud.conllu', "a", encoding="utf-8") as f:
                f.write(sen)


def main():
    with open('chinese_data/bart.train.ctb51.ud.conllu', "r", encoding = "utf-8") as f:
        sents = f.read()
    parse_conllu(sents)


if __name__ == "__main__":
    main()