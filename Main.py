import os
from SentimentAnalysis import (sentiment_analysis,
                               load_create_corpus)
from TimeSeries import(create_Returns_TS,
                       create_Sentiment_TS)



corpus_data_file = 'corpus_data.pkl'
data_repo = "C:/Users/josep/PycharmProjects/CapstoneProject/DATA"
corpus_data = load_create_corpus(corpus_data_file, data_repo)

LM_pkl = "Loughran-McDonald.pkl"
FEEL_pkl = "FEEL.pkl"
InqB = "./Dictionaries/inquirerbasic_fr.xlsx"
Oil = "./Dictionaries/OIL_ECON_FR.xlsx"
Lexicoder = "lexicoder.pkl"
dic_paths = [LM_pkl, FEEL_pkl, InqB, Oil, Lexicoder]

for dict_path in dic_paths:
    corpus_with_sentiment = sentiment_analysis(corpus_data, dict_path)

returns_fpath = "./FinancialData/CAQReturns.xlsx"
returns_TS = create_Returns_TS(returns_fpath)

# Sentiment
sentiment_fpaths = os.listdir("./output")
sentiment_fpaths_output = []
for fpath in sentiment_fpaths:
    sentiment_fpaths_output.append("./output/"+fpath)

sentiment_TS = create_Sentiment_TS(sentiment_fpaths_output)
sentiment_TS['Returns'] = returns_TS['Return']
sentiment_TS = sentiment_TS.fillna(0)

# Selecting columns to include in the CSV file
columns_to_include = ['Date'] + [col for col in sentiment_TS.columns if 'mean_' in col] + ['Returns']
# Save DataFrame to CSV with selected columns
sentiment_TS[columns_to_include].to_csv('TimeSeries.csv', index=False)