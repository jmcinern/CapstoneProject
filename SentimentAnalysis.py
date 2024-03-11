import os
from CorpusLexisNexis import CorpusLexisNexis
import pandas as pd
import pickle
# Class used to format and normalize dictionaries (lemmatisation).
from DictionaryPreprocessing import (
    load_format_lemmatise_Loughran_McDonald_Dic,
    load_format_lemmatise_lexicoder,
    load_format_lemmatise_Feel,
    load_lemmatise_GI,
    load_lemmatise_Oil_Econ
)


# Use pickle to serialize corpus to prevent creating it each time running the SA
def load_create_corpus(corpus_data_file, data_repo):
    if os.path.exists(corpus_data_file):
        with open(corpus_data_file, 'rb') as f:
            corpus_data = pickle.load(f)
    else:
        corpus = CorpusLexisNexis(data_repo)
        file_names = os.listdir(data_repo)
        corpus_data = corpus.create_corpus(file_names)
        with open(corpus_data_file, 'wb') as f:
            pickle.dump(corpus_data, f)
    return corpus_data


def sentiment_analysis(corpus, dict_path, output_folder='output'):

    if 'Lough' in dict_path:
        dictionary = load_format_lemmatise_Loughran_McDonald_Dic(dict_path)
    elif 'FEEL' in dict_path:
        dictionary = load_format_lemmatise_Feel(dict_path)
    elif 'lexi' in dict_path:
        dictionary = load_format_lemmatise_lexicoder(dict_path)
    elif 'inq' in dict_path:
        dictionary = load_lemmatise_GI(dict_path)
    elif 'OIL' in dict_path:
        dictionary = load_lemmatise_Oil_Econ(dict_path)
    else:
        dictionary = None
        print('error finding dictionary file')

    # Extract and normalize French terms once to reduce time complexity.
    terms_french = dictionary.iloc[:, 1].dropna().tolist()
    terms_french = [item.lower() for item in terms_french]
    sentiment_for_terms = []
    for idx, rows in dictionary.iterrows():
        if dictionary.at[idx, "Positive"] == "Positive":
            sentiment_for_terms.append("Positive")
        elif dictionary.at[idx, "Negative"] == "Negative":
            sentiment_for_terms.append("Negative")
        else:
            sentiment_for_terms.append("None")

    # Create dictionary of French words (key) and their corresponding sentiment score (value)
    french_sentiment = {terms_french[i]: sentiment_for_terms[i] for i in range(len(terms_french))}
    # Create a list to store sentiment scores and counts of positive and negative words
    time_series_data = []


    # Iterate through articles in the corpus
    for country, articles in corpus.items():
        for article in articles:
            tokens = article["tokens"]
            date = article["date"]
            newspaper = article["newspaper"]
            num_tokens = article["num_tokens"]
            title = article["title"]

            # Perform sentiment analysis using the dictionary
            sentiment_score, positive_count, negative_count, positive_words, negative_words = calculate_sentiment(tokens, french_sentiment)

            # Normalize sentiment scores by article length
            sentiment_normalized = sentiment_score / num_tokens


            # Append selected information to the time series data
            time_series_data.append({
                "Country": country,
                "Newspaper": newspaper,
                "Title": title,
                "Sentiment": sentiment_normalized,
                "Date": date,
                "Num_tokens": num_tokens,
                "Positive_count": positive_count,
                "Negative_count": negative_count,
                "Tokens": tokens,
                "Positive_Words": positive_words,
                "Negative_Words": negative_words
            })

    # Convert time_series_data to a DataFrame for easier manipulation
    time_series_df = pd.DataFrame(time_series_data)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Write the selected columns to a CSV file
    output_file_path = os.path.join(output_folder, f'sentiment_analysis_results_{os.path.basename(dict_path)}.csv')
    time_series_df.to_csv(output_file_path, index=False,
                          columns=["Country", "Newspaper", "Title", "Sentiment", "Date", "Num_tokens", "Positive_count",
                                   "Negative_count"],
                          encoding='utf-8-sig')

    return corpus, time_series_data


# tokens : list of tokens in article,
# fr_sentiment : dictionary - keys: french terms, values: sentiment score ('Negative'/'Positive')
def calculate_sentiment(tokens, fr_sentiment):
    positive_count = 0
    negative_count = 0
    positive_words = []
    negative_words = []
    for group_size in range(1, 4):
        # Iterate over the list of tokens in groups of 5
        for token_group in zip(*[tokens[i:] for i in range(group_size)]):
            token_phrase = " ".join(token_group)
            # print(f"TOKEN: {token}")
            # sentiment = "None" if no token found, otherwise "Negative"/"Positive"
            sentiment = fr_sentiment.get(token_phrase, "None")
            # update sentiment polarity counts
            if sentiment == "Positive":
                print(f"{token_group} is positive")
                positive_count += 1
                positive_words.append(token_phrase)
            elif sentiment == "Negative":
                print(f"{token_group} is negative")
                negative_count += 1
                negative_words.append(token_phrase)
            elif sentiment != "None":
                print("error accessing sentiment score in french_sentiment dictionary")

    # Calculate sentiment score as the difference between the number of positive and negative tokens, score will be
    # positive if more positive tokens and negative if more negative tokens.
    sentiment_score = positive_count - negative_count
    # print(sentiment_score)

    return sentiment_score, positive_count, negative_count, positive_words, negative_words

def show_SA(corpus_with_sentiment, dict_path):
    dict_path = os.path.basename(dict_path)

    for i in range(10):
        SA_representation = pd.DataFrame({
            "Title": [],
            "Sentiment": [],
            "Text": [],
            "Positive_Words": [],
            "Negative_Words": []
        })
        titles = []
        sentiments = []
        texts = []
        pos_words = []
        neg_words = []
        corpus, TS = corpus_with_sentiment
        for row in TS:
            text = row['Tokens']
            text = " ".join(text)
            titles.append(row['Title'])
            sentiments.append(row['Sentiment'])
            texts.append(text)
            pos_words.append(row['Positive_Words'])
            neg_words.append(row['Negative_Words'])


        SA_representation['Title'] = titles
        SA_representation['Text'] = texts
        SA_representation['Sentiment'] = sentiments
        SA_representation['Positive_Words'] = pos_words
        SA_representation['Negative_Words'] = neg_words

        SA_representation.to_csv("./Display/Display10"+dict_path+".csv", encoding='utf-8-sig')


'''
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
'''




