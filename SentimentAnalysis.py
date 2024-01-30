import os
import nltk
from nltk.tokenize import word_tokenize
from CorpusLexisNexis import CorpusLexisNexis
import pandas as pd

# Download the 'punkt' resource
nltk.download('punkt')


# Funcition to find the longest french term (number of spaces) for match and search with tokens in text


def sentiment_analysis(corpus, dict_path, output_folder='output'):
    # Open the dictionary file
    dictionary = pd.read_excel(dict_path)
    column_names = list(dictionary.columns)

    # Extract and normalize French terms once to reduce time complexity.
    terms_french = dictionary.iloc[:, 1].dropna().tolist()
    terms_french = [item.lower() for item in terms_french]

    # Create a list to store sentiment scores and counts of positive and negative words
    time_series_data = []

    # Iterate through articles in the corpus
    for country, articles in corpus.items():
        for article in articles:
            text = article["text"]
            date = article["date"]
            newspaper = article["newspaper"]
            num_tokens = article["num_tokens"]
            title = article["title"]

            # Tokenize the text
            tokens = []
            for sentence in text:
                tokens.extend(word_tokenize(sentence.lower()))

            # Perform sentiment analysis using the dictionary
            sentiment_scores, positive_count, negative_count = calculate_sentiment(tokens,
                                                                                   dictionary,
                                                                                   column_names,
                                                                                   terms_french)

            # Normalize sentiment scores by article length
            for key in sentiment_scores:
                sentiment_scores[key] /= num_tokens

            # Append selected information to the time series data
            time_series_data.append({
                "Country": country,
                "Newspaper": newspaper,
                "title": title,
                "sentiment": sentiment_scores["overall"],
                "date": date,
                "num_tokens": num_tokens,
                "positive_count": positive_count,
                "negative_count": negative_count
            })

    # Convert time_series_data to a DataFrame for easier manipulation
    time_series_df = pd.DataFrame(time_series_data)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Write the selected columns to a CSV file
    output_file_path = os.path.join(output_folder, f'sentiment_analysis_results_{os.path.basename(dict_path)}.csv')
    time_series_df.to_csv(output_file_path, index=False,
                          columns=["Country", "Newspaper", "title", "sentiment", "date", "num_tokens", "positive_count",
                                   "negative_count"],
                          encoding='utf-8-sig')

    return corpus, time_series_data


def calculate_sentiment(tokens, dictionary, column_names, terms_french):
    # Initialize sentiment scores and counts
    sentiment_scores = {column: 0 for column in column_names}
    positive_count = 0
    negative_count = 0

    # Define positive and negative keys
    positive_keys = ['Positive', 'FinPos', 'Positiv']
    negative_keys = ['Negative', 'FinNeg', 'Negativ']

    # dictionary to prioritise multi-tokens when they are triggered in the same place in the text as
        # as a unitoken
    multitoken_pos = set()
    pos_multi = 0
    # Check for multi-token phrases and update sentiment scores
    for token_index, token in enumerate(tokens):
        for i in range(4, 0, -1):  # Adjust the range as needed
            if token_index - i >= 0:
                multi_token = " ".join(tokens[token_index - i:token_index + 1])
                if multi_token in terms_french:
                    multitoken_pos.update(range(token_index - i, token_index + 1))
                    term_index = terms_french.index(multi_token)
                    for column in column_names:
                        if dictionary.at[term_index, column] == column:
                            sentiment_scores[column] += 1

                            # Check if the category is positive or negative and increment the counts accordingly
                            if any(key in column for key in positive_keys):
                                positive_count += 1
                            elif any(key in column for key in negative_keys):
                                negative_count += 1
                                #print(f"negative: {multi_token}")
        pos_multi += +1

    pos_uni = 0
    # Iterate over each token
    for token_index, token in enumerate(tokens):
        #print(f"token: {token}, pos uni: {pos_uni}, pos multi: {multitoken_pos}")
        # Check if the token is present in the terms_french list
        if token in terms_french and pos_uni not in multitoken_pos:
            # Get the index of the token in the terms_french list
            term_index = terms_french.index(token)
            # Increment sentiment scores for all respective categories
            for column in column_names:
                if dictionary.at[term_index, column] == column:
                    sentiment_scores[column] += 1

                    # Check if the category is positive or negative and increment the counts accordingly
                    if any(key in column for key in positive_keys):
                        positive_count += 1
                        print(f"positive: {token}")
                    elif any(key in column for key in negative_keys):
                        negative_count += 1
                        #print(f"negative: {token}")
        pos_uni += 1

    # Calculate an overall sentiment score based on the difference between positive and negative terms
    sentiment_scores["positive"] = sum(sentiment_scores.get(key, 0) for key in positive_keys)
    sentiment_scores["negative"] = sum(sentiment_scores.get(key, 0) for key in negative_keys)
    sentiment_scores["overall"] = sentiment_scores["positive"] - sentiment_scores["negative"]

    return sentiment_scores, positive_count, negative_count


# run code
corpus = CorpusLexisNexis('./DATA/')
# List of corpus files by country
# Repository where papers are stored.
data_repo = "C:/Users/josep/PycharmProjects/CapstoneProject/DATA"
file_names = os.listdir(data_repo)
# Create corpus based on data
corpus_data = corpus.create_corpus(file_names)

dictionaries_folder = 'Dictionaries/'
dictionary_files = os.listdir(dictionaries_folder)
excel_files = [file for file in dictionary_files if file.endswith('.xlsx')]
dictionary_paths = [os.path.join(dictionaries_folder, file) for file in excel_files]

for dict_path in dictionary_paths:
    if 'OIL' in dict_path:
        print(dict_path)
        corpus_with_sentiment = sentiment_analysis(corpus_data, dict_path)