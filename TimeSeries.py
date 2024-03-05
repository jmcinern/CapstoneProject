import pandas as pd
import os
import numpy as np

# Create Returns Time Series
def create_Returns_TS(fpath_returns):

    # Initialise TS and columns
    returns_TS = pd.read_excel(fpath_returns)
    dates = []
    returns = []

    # function to get an array of dates in range passed as parram: start, end, YYYY-MM-DD
    dates = pd.date_range(start="2022-01-01", end="2023-12-31", normalize=True)

    # Get returns, set to 0 if no date available (weekends, start)
    for date in dates:
        if date.strftime('%Y-%m-%d') in returns_TS['Date'].dt.strftime('%Y-%m-%d').values:
            return_for_date = returns_TS.loc[returns_TS['Date'] == date, 'CAQ Daily Return'].iloc[0]
            if pd.isna(return_for_date):
                return_for_date = 0
        else:
            return_for_date = 0
        returns.append(return_for_date)

    returns_TS = pd.DataFrame({
        'Date': dates,
        'Return': returns
    })
    return returns_TS

# Creates time series of sentiment scores. ['Date' 'Country(i)_Dictionary(j).... 'Country(I)_Dictionary(J)']
def get_sentiment_by_country_group(dates, country_group):
    dates_sentiment = {
        'Date': dates,
        'Sentiment': []
    }
    country_group['Date'] = pd.to_datetime(country_group['Date'], format='%d/%m/%Y')

    for date in dates:
        sentiment_for_date = country_group.loc[country_group['Date'] == date, 'Sentiment']
        mean_sentiment_for_date = sentiment_for_date.mean()

        dates_sentiment['Sentiment'].append(mean_sentiment_for_date)

    return dates_sentiment
def create_Sentiment_TS(sentiment_fpaths):
    dates = pd.date_range(start="2022-01-01", end="2023-12-31", normalize=True)
    sentiment_TS = pd.DataFrame({'Date': dates})
    # Get columns dict and then country. Eg: sentiment_analysis_results_inquirerbasic_fr.xlsx.csv
    start_of_dic_pos = 1
    for sentiment_dic_fpath in sentiment_fpaths:
        sentiment_TS_for_dic = pd.read_csv(sentiment_dic_fpath)

        # Get name of dictionary from file name
        dic_name = get_dic_name(sentiment_dic_fpath)

        # Column for mean sentiment by country for dictionary
        mean_sentiment_col = "mean_" + dic_name

        # Group data by country 'Country' column values.
        sentiment_TS_by_country = sentiment_TS_for_dic.groupby('Country')
        num_countries = sentiment_TS_for_dic.groupby('Country').ngroups

        for country, country_group in sentiment_TS_by_country:
            col_name = dic_name + "_" + country
            sentiment_for_dates = get_sentiment_by_country_group(dates, country_group)
            sentiment_TS[col_name] = sentiment_for_dates['Sentiment']

        sentiment_mean_for_dic = sentiment_TS.iloc[:, start_of_dic_pos:start_of_dic_pos+num_countries].mean(axis=1)
        sentiment_TS[mean_sentiment_col] = sentiment_mean_for_dic
        # Account for new mean col
        num_countries = num_countries + 1
        start_of_dic_pos = start_of_dic_pos + num_countries

    return sentiment_TS
def get_dic_name(sentiment_dic_fpath):
    split_dicpath = sentiment_dic_fpath.split("/output/sentiment_analysis_results_")
    dicname_with_filetype = split_dicpath[1]
    split_dic_name = dicname_with_filetype.split(".")
    dic_name = split_dic_name[0]
    return dic_name

# Run code
# Returns
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




