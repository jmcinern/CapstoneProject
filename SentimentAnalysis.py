import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
from CorpusLexisNexis import CorpusLexisNexis  # Import the CorpusLexisNexis class from your file

# Download the 'punkt' resource
nltk.download('punkt')

# Takes the corpus (of news articles) and a semantic dictionary and then performs a sentiment analysis.
def sentiment_analysis(corpus, dict_path, output_folder='output'):
    # Open the dictionary file
    dictionary = pd.read_excel(dict_path)
    column_names = list(dictionary.columns)

    # Create a list to store sentiment scores and dates for the time series graph
    time_series_data = []

    # Iterate through articles in the corpus
    for country, articles in corpus.items():
        for article in articles:
            text = article["text"]
            date = article["date"]  # Assuming there is a "date" field in your article
            title = article["title"]
            # Tokenize the text
            tokens = word_tokenize(text.lower())

            # Perform sentiment analysis using the dictionary
            sentiment_score = analyze_sentiment(tokens, dictionary, column_names)

            # Append sentiment score and date to the time series data
            time_series_data.append({"country": country, "date": date, "sentiment": sentiment_score})

            # Assign the sentiment score to the article
            article["sentiment"] = sentiment_score

    # Convert time_series_data to a DataFrame for easier manipulation
    time_series_df = pd.DataFrame(time_series_data)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Write the time_series_data to a CSV file
    output_file_path = os.path.join(output_folder, f'sentiment_analysis_results_{os.path.basename(dict_path)}.csv')
    time_series_df.to_csv(output_file_path, index=False)

    return corpus, time_series_data


def analyze_sentiment(tokens, dictionary, column_names):
    # Initialize sentiment scores
    sentiment_scores = {column: 0 for column in column_names}

    # Extract terms from the first column of the dictionary
    terms_french = dictionary.iloc[:, 1].dropna().tolist()
    # Normalize French terms to match with already normalized tokens.
    terms_french = [item.lower() for item in terms_french]

    for token in tokens:
        if token in terms_french:
            # Find the index of the matching term in the French terms list, categories this word falls under
            term_index = terms_french.index(token)

            # Increment sentiment scores for all respective categories
            for column in column_names:
                if dictionary.at[term_index, column] == column:
                    sentiment_scores[column] += 1

    # Calculate an overall sentiment score based on the difference between positive and negative terms
    print(sentiment_scores)
    positive_keys = ['Positive', 'FinPos', 'Positiv']
    negative_keys = ['Negative', 'FinNeg', 'Negativ']

    positive_score = sum(sentiment_scores.get(key, 0) for key in positive_keys)
    negative_score = sum(sentiment_scores.get(key, 0) for key in negative_keys)
    overall_sentiment_score = positive_score - negative_score

    return overall_sentiment_score


# Example usage
corpus = CorpusLexisNexis('./DATA/')
file_list = ['IvoryCoast500']
corpus_data = corpus.create_corpus(file_list)

# Specify the path to the dictionaries folder
dictionaries_folder = 'Dictionaries/'
# Get a list of all files in the dictionaries folder
dictionary_files = os.listdir(dictionaries_folder)
# Filter only the Excel files in the folder
excel_files = [file for file in dictionary_files if file.endswith('.xlsx')]
# Create a list of dictionary paths by joining the folder path with each file name
dictionary_paths = [os.path.join(dictionaries_folder, file) for file in excel_files]

for dict_path in dictionary_paths:
    corpus_with_sentiment, time_series_data = sentiment_analysis(corpus_data, dict_path)
