import datetime
import os
import re
import spacy
class CorpusLexisNexis:

    def __init__(self, data_location):
        #Get paper names based on file names
        paper_names = []
        # Repository where papers are stored.
        data_repo = "C:/Users/josep/PycharmProjects/CapstoneProject/Data"
        file_names = os.listdir(data_repo)
        for fn in file_names:
            country_paper = (fn.split("_"))
            paper = country_paper[1].rstrip(".txt")
            paper_names.append(paper)

        self.data_location = data_location
        # List of paper names
        self.paper_names = paper_names

    def _is_month(self, word):
        # Check if the word represents a month
        french_months = [
            'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
        ]
        english_months = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]

        return word.lower() in (french_months + english_months)

    def _is_year(self, word):
        # Check if the word represents a year
        return word.isdigit() and len(word) == 4

    def _files_to_corpus(self, file_name, nlp):
        # Use list of France related words to only add articles with these words in title.
        france_related_words = ['france', 'hexagone', 'paris', 'macron', 'marseille', 'français', 'française',
                                'françaises', 'franco']
        title_list = []
        file_path = os.path.join(self.data_location, file_name)

        # Dictionary to map French month names to numeric values
        fr_and_en_month_mapping = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }

        # Create a list to store articles
        articles = []

        # Open the TXT file for reading
        with open(file_path, 'r', encoding='utf-8') as file:
            france_related_title = False
            duplicate_title = True
            lines = file.readlines()
            num_lines = len(lines)

            # Initialize variables for the current article
            text = []
            # Bool to signify that we are in the body of the text
            in_body = False
            newspaper = ""
            date = ""
            num_tokens = ""
            title = ""

            # Iterate through lines in the file
            for line_index, line in enumerate(lines):
                line = line.strip()

                # Get number of tokens of article, format: Length: 999 words
                pattern = r'Length: (\d+) words'
                match = re.match(pattern, line)
                if match:
                    num_tokens = int(match.group(1))

                # Check if the line contains the name of any paper
                if any(paper_name == line for paper_name in self.paper_names):
                    # Set the title as the line before the newspaper
                    title_index = max(0, line_index - 1)
                    title = lines[title_index].strip()
                    if title == "":
                        title_index = max(0, line_index - 2)
                        title = lines[title_index].strip()
                        title_list.append(title)
                    newspaper = line

                    # Move to the next line to get the date
                    next_index = min(line_index + 1, num_lines - 1)
                    line = lines[next_index].strip()

                    # Initialize month, day, and year
                    month, day_str, year_str = None, None, None

                    # Check each word in the line to identify date components
                    words = line.split()
                    for word in words:
                        word = word.strip(",")
                        if self._is_month(word):
                            month = fr_and_en_month_mapping.get(word.lower())
                        elif word.isdigit() and len(word) <= 2:
                            day_str = word
                        elif self._is_year(word):
                            year_str = word

                    # Check if all date components are present
                    if month is not None and day_str is not None and year_str is not None:
                        # Parsing and reformatting the date
                        date_object = datetime.datetime.strptime(f"{year_str}-{month:02d}-{int(day_str):02d}",
                                                                 '%Y-%m-%d')
                        date = date_object.strftime('%d/%m/%Y')

                    # Check if any France-related word is present in the title
                    if any(word in title.lower() for word in france_related_words) and title not in title_list:
                        france_related_title = True
                        duplicate_title = False

                if line == 'Body':
                    # Initialize the text list for the article and set in_body to True
                    text = []
                    in_body = True

                if in_body:
                    if line == 'End of Document':
                        # It indicates the end of an article
                        if france_related_title and not duplicate_title:
                            #tokenize text when building corpus to avoid having to do it every time the SA is run
                            # Tokenize the text using spacy NLP model
                            text = " ".join(text)
                            doc = nlp(text)
                            tokens = []

                            for token in doc:
                                if not token.is_space:
                                    # Lemmatise token : token: arrêté
                                    #                   lemma: arrêter
                                    lemma = token.lemma_.lower()
                                    tokens.append(lemma)
                            article = {
                                "tokens": tokens,
                                "title": title,
                                "newspaper": newspaper,
                                "date": date,
                                "num_tokens": num_tokens,
                            }
                            articles.append(article)
                            france_related_title = False

                        in_body = False
                    else:
                        # Append lines to the text list if inside 'Body'
                        text.append(line)
        return articles

    def create_corpus(self, file_names):
        corpus = {}
        # NLP language model trained on french news data.
        nlp = spacy.load("fr_core_news_sm")

        for fn in file_names:
            country_paper = fn.split("_")
            country = country_paper[0]
            articles = self._files_to_corpus(fn, nlp)
            # If the country key already exists in the corpus, append the articles to the existing list
            if country in corpus:
                corpus[country].extend(articles)
            else:
                corpus[country] = articles
        print('Corpus created')
        return corpus

