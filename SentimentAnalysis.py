import CorpusLexisNexis

corpus = CorpusLexisNexis.CorpusLexisNexis('./DATA/')
file_list = ['BurkinaFaso']
corpus = corpus.create_corpus(file_list)
print(corpus)