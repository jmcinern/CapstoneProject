import re
import os

class CorpusLexisNexis:
    def __init__(self, data_location):
        self.data_location = data_location

    def _files_to_corpus(self, country):
        country_path = os.path.join(self.data_location, country)

        # Create a list to store articles
        articles = []

        # Open the TXT file for reading
        with open(country_path, 'r', encoding='utf-8') as file:
            # Initialize variables for the current article
            text = []
            in_body = False
            titles_list = []
            date = ""
            title = ""

            # Iterate through lines in the file
            for line in file:
                line = line.strip()

                if line.startswith("Documents ("):
                    num_docs = int(line.split("(")[1].split(")")[0])

                elif re.match(r'\d+\.\s', line):
                    title = line.split('. ')[1]
                    titles_list.append(title)

                if line in titles_list:
                    title = line
                    # Remove line from titles list
                    titles_list.remove(line)

                if line == 'Body':
                    # Initialize the text list for the article and set in_body to True
                    text = []
                    in_body = True

                if in_body:
                    if line.startswith("Load-Date:"):
                        # Add date article was published
                        date = line.split(":")[1].strip()
                        in_body = False  # Set in_body to False
                    else:
                        # Append lines to the text list if inside 'Body'
                        text.append(line)

                if line == 'End of Document':
                    # It indicates the end of an article
                    article = {
                        "title": title,
                        "date": date,
                        "text": "\n".join(text)  # Join lines to form the article text
                    }
                    articles.append(article)

        return articles

    def create_corpus(self, file_list):
        corpus = {}

        # Iterate over the list of countries
        for country in file_list:
            articles = self._files_to_corpus(country)
            # Store the articles for the current country
            corpus[country] = articles

        return corpus

