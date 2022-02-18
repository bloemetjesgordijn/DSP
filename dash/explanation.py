general = '''This tool is designed to uncover modus operandi in the production of synthetic drugs by analyzing precursor and drug prevalence. 
This tool used data scraped from uitspraken.rechtspraak.nl. Currently for development and speed purposes it is limited to 5000 case results.
The UI consists of 8 elements:

'''
elements = ['Interactive graph: You can zoom in, select lines and take screenshots. If you click on a line, it queries what cases make up that specific data point.'
,'Rolling mean slider: transforms the data to use a moving average. Every datapoint is now the average of the past x datapoints.'
,'Court mentions: This is the main attraction. Select precursors/drugs you want to analyze. For every item, synonyms and chemical compound are included.'
,'Sewage data: Sewage data from the EMCDDA. If included, y axis is not mentions, but doses per person per capita per year.'
,'Extra terms: Here you can enter custom extra terms. Type in something and either enter or click away, and then a checkbox appears. This checkbox works the same as the court mentions. The delete button deletes all extra terms. This functionality enables this tool to be used for other purposes as  well, not just precursors/drugs.'
,'Correlation matrix: When there are 2 or more lines plotted (sewage data not included) you can create a correlation matrix. This uses Pearsons correlation.'
,'Find cases by Mentions: Find specific cases that exceed x mentions for term y. You can for example search for cases that mention XTC more than 10 times.']