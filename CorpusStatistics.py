import pandas as pd
import xlsxwriter

# Assuming df is your DataFrame
df = pd.read_excel('./DATA/CorpusStats2.xlsx')

# Create a nested dictionary to store data for each newspaper over the years per country
newspaper_data_by_country = {country: {} for country in df['Country'].unique()}

# Group the data by 'Country,' 'Newspaper,' and 'Year Key Word'
grouped_data_key_word = df.groupby(['Country', 'Newspaper', 'Year Key Word'])

# Iterate over groups to populate the dictionary for Key Word Hits
for (country, newspaper, year_key_word), group in grouped_data_key_word:
    total_hits_key_word = group['Key Word Hits'].sum()
    year_key_word_str = str(year_key_word)

    # Initialize the dictionary if not present
    if country not in newspaper_data_by_country:
        newspaper_data_by_country[country] = {}

    if newspaper not in newspaper_data_by_country[country]:
        newspaper_data_by_country[country][newspaper] = {}

    # Set 'Key Word Hits' for the specified year
    newspaper_data_by_country[country][newspaper][year_key_word_str] = {'Key Word Hits': total_hits_key_word}

# Group the data by 'Country,' 'Newspaper,' and 'Year Total'
grouped_data_total = df.groupby(['Country', 'Newspaper', 'Year Total'])

# Iterate over groups to populate the dictionary for Total Hits
for (country, newspaper, year_total), group in grouped_data_total:
    total_hits_total = group['Total Hits'].sum()
    year_total_str = str(year_total)
    if country in newspaper_data_by_country and newspaper in newspaper_data_by_country[country]:
        if year_total_str in newspaper_data_by_country[country][newspaper]:
            newspaper_data_by_country[country][newspaper][year_total_str]['Total Hits'] = total_hits_total
        else:
            newspaper_data_by_country[country][newspaper][year_total_str] = {'Total Hits': total_hits_total}

# Calculate the proportion for each year for each country and newspaper
for country in newspaper_data_by_country:
    for newspaper in newspaper_data_by_country[country]:
        for year_key_word, data in newspaper_data_by_country[country][newspaper].items():
            key_word_hits = data.get('Key Word Hits', 0)
            total_hits = data.get('Total Hits', 0)

            if total_hits != 0:
                proportion = key_word_hits / total_hits
                newspaper_data_by_country[country][newspaper][year_key_word]['Proportion'] = proportion

# Create DataFrames for the three outputs
average_proportion_per_year = []
country_average_proportion = []
country_proportion_per_year = []

# Calculate average proportion per year
for year in sorted(set(year for data in newspaper_data_by_country.values() for newspaper, years in data.items() for year in years.keys())):
    proportions = [newspaper_data_by_country[country][newspaper].get(year, {}).get('Proportion', 0) for country in newspaper_data_by_country for newspaper in newspaper_data_by_country[country]]
    non_zero_proportions = [proportion for proportion in proportions if proportion != 0]
    if non_zero_proportions:
        average_proportion = sum(non_zero_proportions) / len(non_zero_proportions)
        average_proportion_per_year.append({'Year': pd.to_datetime(year).year, 'Average Proportion': average_proportion})

# Calculate country-average proportion
for country, data in newspaper_data_by_country.items():
    country_proportions = [newspaper_data_by_country[country][newspaper].get(year, {}).get('Proportion', 0) for newspaper in data for year in data[newspaper]]
    non_zero_country_proportions = [proportion for proportion in country_proportions if proportion != 0]
    if non_zero_country_proportions:
        average_country_proportion = sum(non_zero_country_proportions) / len(non_zero_country_proportions)
        country_average_proportion.append({'Country': country, 'Average Proportion': average_country_proportion})

# Calculate country-proportion per year
for country, data in newspaper_data_by_country.items():
    for newspaper, years in data.items():
        for year, values in years.items():
            key_word_hits = values.get('Key Word Hits', 0)
            total_hits = values.get('Total Hits', 0)
            proportion = values.get('Proportion', 0)
            if total_hits != 0:
                country_proportion_per_year.append({'Country': country, 'Newspaper': newspaper, 'Year': pd.to_datetime(year).year, 'Key Word Hits': key_word_hits, 'Total Hits': total_hits, 'Proportion': proportion})

# Create DataFrames
df_average_proportion_per_year = pd.DataFrame(average_proportion_per_year)
df_country_average_proportion = pd.DataFrame(country_average_proportion)
df_country_proportion_per_year = pd.DataFrame(country_proportion_per_year)

# Write DataFrames to the same Excel file with different sheets
with pd.ExcelWriter('OtherFiles/proportion_analysis.xlsx', engine='xlsxwriter') as writer:
    df_average_proportion_per_year.to_excel(writer, sheet_name='Average Proportion per Year', index=False)
    df_country_average_proportion.to_excel(writer, sheet_name='Country Average Proportion', index=False)
    df_country_proportion_per_year.to_excel(writer, sheet_name='Country Proportion per Year', index=False)
