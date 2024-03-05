import pickle
import os
import pandas as pd
import spacy

# Function that lemmatizes the French words using spaCy lemmatisation.
nlp = spacy.load("fr_core_news_sm")

# Set of functions that convert dictionaries to General Inquirer format. With Columns:
# English word, French word, Positive, Negative
# Where French words will have either 'Positive', 'Negative' or 0 representing their sentiment.
def LMcD_to_GI():
    # Read Loughran-McDonald dictionary
    dictionary = pd.read_excel("./Dictionaries/Loughran-McDonald_DIC.xlsx")
    print('converting lm to gi')
    # Iterate over each row
    for index, row in dictionary.iterrows():
        # remove multitoken terms
        term = row['French Translation']
        if not ("'" in term or " " in term):
            for col in ['Negative', 'Positive']:
                # If value is not 0, replace it with the column name
                if row[col] != 0:
                    print('senitment maxxxin')
                    dictionary.at[index, col] = col

    return dictionary

# converts FEEL dictionary to GQ format to facilitate SA
def FEEL_to_GI():
    dictionary = pd.read_excel("./Dictionaries/FEEL_UFT8.xlsx")
    # FEEL has one column ['polarity'] that contains cells either 'positive' or 'negative'
    # add two columns to dictionary: ['Positive'] and ['Negative']
    positive_col = []
    negative_col = []
    for index, row in dictionary.iterrows():
        if row['polarity'] == 'positive':
            positive_col.append('Positive')
            negative_col.append(0)
        elif row['polarity'] == 'negative':
            negative_col.append('Negative')
            positive_col.append(0)

    # append negative and positive list to respective columns
    dictionary['Positive'] = positive_col
    dictionary['Negative'] = negative_col
    return dictionary

def lexicoder_to_GI():
    words = []
    positive_list = []
    negative_list = []
    # Blank list to maintain formatting where English words are in GI dictionary.
    blank_list = []
    with open('./Dictionaries/lexicoder', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            if line.startswith("+positive"):
                sentiment = "Positive"
                # skip this line so as not to add sentiment to words list
                continue
            elif line.startswith("+negative"):
                sentiment = "Negative"
                continue
            else:
                # Append data to lists
                words.append(line.replace("*", ''))
                if sentiment == "Positive":
                    positive_list.append("Positive")
                    negative_list.append(0)
                    blank_list.append(0)
                elif sentiment == "Negative":
                    positive_list.append(0)
                    negative_list.append("Negative")
                    blank_list.append(0)


        df = pd.DataFrame({
            "Blank": blank_list,
            "Words": words,
            "Negative": negative_list,
            "Positive": positive_list
        })
        return df


def lemmatise_dic(dic_formatted, nlp):
    # Lemmatise french column
    french_words_lemmatised = []
    # French words in first col
    french_words = dic_formatted.iloc[:, 1].tolist()
    # to string
    french_words_text = " ".join(french_words)
    # tokenise
    doc = nlp(french_words_text)
    for term in french_words:
        term_tokenized = nlp(term)
        if len(term_tokenized) == 1:
            # lemmatise the single token, loop just to make sure that token is of type spaCy token
                for token in term_tokenized:
                    lemma = token.lemma_.lower()
                    print(f"lemma: {lemma}")
                    # print(f"lemma: {lemma}")
                    french_words_lemmatised.append(lemma)
        # remove multitoken term from dictionary
        else:
            french_words_lemmatised.append("multitokenremoved")
    # replace original column with lemmatised column
    dic_formatted.iloc[:, 1] = french_words_lemmatised
    dic_formatted_and_lemmatised = dic_formatted
    print('Outputting dic to display')
    dic_formatted_and_lemmatised.to_csv("./Display/testLemma")
    return dic_formatted_and_lemmatised



# Set of functions that serialise the GI formatted dictionaries to avoid having to format them each time the
# sentiment analysis is run.
def load_format_Loughran_McDonald_Dic(dic_fpath):
    if os.path.exists(dic_fpath):
        print('pkl already exists')
        with open(dic_fpath,'rb') as f:
            dic_formatted = pickle.load(f)
    else:
        print('preprosseing dic')
        # format
        dic_formatted = LMcD_to_GI()
        # lemmatise
        dic_lemmatised_and_formatted = lemmatise_dic(dic_formatted, nlp)
        with open(dic_fpath, 'wb') as f:
            pickle.dump(dic_lemmatised_and_formatted, f)
    return dic_formatted

def load_format_Feel(dic_fpath):
    if os.path.exists(dic_fpath):
        with open(dic_fpath,'rb') as f:
            dic_formatted = pickle.load(f)
    else:
        dic_formatted = FEEL_to_GI()
        dic_lemmatised_and_formatted = lemmatise_dic(dic_formatted, nlp)
        with open(dic_fpath, 'wb') as f:
            pickle.dump(dic_lemmatised_and_formatted, f)
    return dic_formatted

def load_format_lexicoder(dic_fpath):
    if os.path.exists(dic_fpath):
        with open(dic_fpath,'rb') as f:
            dic_formatted = pickle.load(f)
    else:
        dic_formatted = lexicoder_to_GI()
        dic_lemmatised_and_formatted = lemmatise_dic(dic_formatted, nlp)
        with open(dic_fpath, 'wb') as f:
            pickle.dump(dic_lemmatised_and_formatted, f)
    return dic_formatted


#load_format_Loughran_McDonald_Dic("Loughran-McDonald.pkl")
#load_format_lexicoder("lexicoder.pkl")
