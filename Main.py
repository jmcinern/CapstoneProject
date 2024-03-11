import os
from SentimentAnalysis import (sentiment_analysis,
                               load_create_corpus,
                               show_SA)
from TimeSeries import(create_financial_TS,
                       create_Sentiment_TS)



corpus_data_file = 'corpus_data.pkl'
data_repo = "C:/Users/josep/PycharmProjects/CapstoneProject/DATA"
corpus_data = load_create_corpus(corpus_data_file, data_repo)

LM_pkl = "Loughran-McDonald.pkl"
FEEL_pkl = "FEEL.pkl"
InqB = "inquirerbasic_fr.pkl"
Oil = "OIL_ECON_FR.pkl"
Lexicoder = "lexicoder.pkl"
dic_paths = [Oil, InqB, FEEL_pkl, Lexicoder, LM_pkl]

for dict_path in dic_paths:
    corpus_with_sentiment = sentiment_analysis(corpus_data, dict_path)
    show_SA(corpus_with_sentiment, dict_path)


financial_fpath = "./FinancialData/CAQReturns.xlsx"
financial_TS = create_financial_TS(financial_fpath)

# Sentiment
sentiment_fpaths = os.listdir("./output")
sentiment_fpaths_output = []
for fpath in sentiment_fpaths:
    sentiment_fpaths_output.append("./output/"+fpath)

sentiment_TS = create_Sentiment_TS(sentiment_fpaths_output)
sentiment_TS['Returns'] = financial_TS['Return']
sentiment_TS['Volume'] = financial_TS['Volume']
sentiment_TS = sentiment_TS.fillna(0)


# Selecting columns to include in the CSV file
columns_to_include = ['Date'] + [col for col in sentiment_TS.columns if 'mean_' in col] + ['Returns'] + ['Volume']
# Save DataFrame to CSV with selected columns
sentiment_TS[columns_to_include].to_csv('TimeSeries.csv', index=False)