
import get_data
import pandas as pd


merged_df = get_data.full_data()


def count_mentions(word_arr):
    dates = []
    counts = []
    uitspraakdata = []
    ids = []
    for i in range(len(merged_df)):
        current = merged_df.iloc[i]
        current_date = current["Uitspraakdatum"]
        current_case_text = current['Case Text']
        current_uitspraakdatum = current['Uitspraakdatum']
        current_case_id = current['Case ID']
        occurrences = 0
        for i in word_arr:
            occurrences = occurrences + current_case_text.lower().count(i.lower())
        if occurrences > 0:
            dates.append(current_date)
            counts.append(occurrences)
            uitspraakdata.append(current_uitspraakdatum)
            ids.append(current_case_id)

    dates = pd.Series(dates)
    counts = pd.Series(counts)
    frame = { 'date': dates, 'count': counts, 'date': uitspraakdata, 'id': ids}
    results = pd.DataFrame(frame)
    return results

def count_cases(word_arr):
    dates = []
    counts = []
    uitspraakdata = []
    ids = []
    for i in range(len(merged_df[:5000])):
        current = merged_df.iloc[i]
        current_date = current['Uitspraakdatum']
        current_case_text = current['Case Text']
        current_uitspraakdatum = current['Uitspraakdatum']
        current_case_id = current['Case ID']
        occurrences = 0
        if any(x.lower() in current_case_text.lower() for x in word_arr):
            occurrences = 1
        if occurrences > 0:
            dates.append(current_date)
            counts.append(occurrences)
            uitspraakdata.append(current_uitspraakdatum)
            ids.append(current_case_id)
    
    dates = pd.Series(dates)
    counts = pd.Series(counts)
    frame = { 'date': dates, 'count': counts, 'date': uitspraakdata, 'id': ids}
    results = pd.DataFrame(frame)
    return results


def get_line(keywords, type):
    if type == 'mentions':
        results = count_mentions(keywords)
    elif type == 'cases':
        results = count_cases(keywords)
    results.set_index('date', inplace=True)
    results.index = pd.to_datetime(results.index)
    monthly_results = results.resample('1M').sum()
    return monthly_results

def get_case_that_exceed_count(word_arr, count):
    case_id = []
    all_occurrences = []
    all_dates = []
    result = []
    for i in range(len(merged_df)):
        current = merged_df.iloc[i]
        current_case_text = current['Case Text']
        current_date = current["Uitspraakdatum"]
        occurrences = 0
        for i in word_arr:
            occurrences = occurrences + current_case_text.lower().count(i.lower())
        if(occurrences >= count):
            parsedId = current['Case ID'].replace('-', ':')
            all_occurrences.append(occurrences)
            case_id.append(parsedId)
            all_dates.append(current_date)
            result = [all_occurrences, case_id, all_dates]

    return result


