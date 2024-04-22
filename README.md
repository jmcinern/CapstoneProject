This repository is the code used for the completion of my final year project. The following is a visual overview of the project.
![image](https://github.com/jmcinern/CapstoneProject/assets/72273070/60b1a4ea-b2cd-4e2a-9109-71b0feb94f4f)


Abstract of thesis:
This project investigates the relationship between sentiment expressed in news media from
Francophone Africa towards France and its impact on the French stock market.

A French language corpus of 1,678,267 words across 52 newspapers and 23 countries was
collected and constructed. The negative sentiment of these articles was measured over the
time span 2022-2023. 5 different sentiment lexicons were used to compare their negative
sentiment measurement’s impact on the French stock market.

Financial data from the CAC 40 French financial index was also collected, and the impact of
the negative sentiment on the financial market was statistically evaluated using multivariate
vector autoregressive econometric models.

The negative sentiment measurements of each lexicon were compared, and it was found
that the lexicons designed for analysing financial media appear to be more appropriate in de-
tecting a relationship between the negative sentiment news media proxies and financial market
proxies.
ii


- DATA: stores files of news articles downloaded from LexisNexis.
- Dictionaries: Stores the sentiment lexicon used for reference in sentiment analysis.
- Display: Provides functionality to view sentiment analysis of articles (not included in main, used for testing purposed)
- Financial Data: Stores the financial data accessed from Yahoo! finance of the CAC 40 historical data in 2022/2023.
- Other Files: files not relevant but views or tested at various stages of the project
- Test: class used for testing output of small samples, no used in final project code.
- Output: output of sentiment time series after analysing corpus using lexicons (dictionaries)
- Sorted dictionaries: Not used in final code, was used in testing faster lexicon (dictionary) lookup
- CorpusLexisNexis.py, creates corpus of news articles from LexisNexis files.
- CorpusStatistics.py, was used in testing to generate stats of corpus
- DictionaryPreprocessing.py: lemmatzes, formats, lowercases, serializes lexicons (dictionaries) used.
- TimeSeries.py: generates time series of negative sentiment and financial markets.
- TimeSeries.csv: File used when running VAR statistical evaluation in GRETL.
