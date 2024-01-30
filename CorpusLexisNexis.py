import datetime
import os
import re
class CorpusLexisNexis:
    def __init__(self, data_location):
        #Get paper names based on file names
        paper_names = []
        # Repository where papers are stored.
        data_repo = "C:/Users/josep/PycharmProjects/CapstoneProject/DATA"
        file_names = os.listdir(data_repo)
        for fn in file_names:
            country_paper = (fn.split("_"))
            paper = country_paper[1]
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

    def _files_to_corpus(self, file_name):
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


                if line == 'Body':
                    # Initialize the text list for the article and set in_body to True
                    text = []
                    in_body = True

                if in_body:
                    if line == 'End of Document':
                        # It indicates the end of an article
                        article = {
                            "text": text,
                            "title": title,
                            "newspaper": newspaper,
                            "date": date,
                            "num_tokens": num_tokens,
                        }
                        articles.append(article)
                        in_body = False
                    else:
                        # Append lines to the text list if inside 'Body'
                        text.append(line)

        return articles

    def create_corpus(self, file_names):
        corpus = {}

        for fn in file_names:
            country_paper = fn.split("_")
            country = country_paper[0]
            articles = self._files_to_corpus(fn)
            # If the country key already exists in the corpus, append the articles to the existing list
            if country in corpus:
                corpus[country].extend(articles)
            else:
                corpus[country] = articles

        return corpus

