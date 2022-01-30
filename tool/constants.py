DRUGS_AND_PRECURSORS = {
    "safrol": ['safrol', 'isosafrol', 'safrool', 'isosafrool'],
    "piperonal": ['piperonal', 'piperonalglycidaat'],
    "PMK": ['PMK','piperonylmethylketon'],
    "BMK": ['BMK', 'BenzylMethylKeton'],
    "apaan": ['apaan','Alpha-Phenylacetoacetonitrile', 'AlphaPhenylacetoacetonitrile'],
    "GBL": ['GBL', 'Gamma-butyrolacton'],
    "MDP2P": ['MDP2P'],
    "efedrine": ['Efedrine', 'Ephedrine'],
    "ergotamine": ['Ergotamine'],
    "lyserginezuur": ['Lyserginezuur'],
    "methamphetamine": ['Methamfetamine', 'Methamphetamine'],
    "MDMA": ['MDMA', 'Methylenedioxymethamphetamine'],
    "amphetamine": ['Amfetamine', 'Amphetamine'],
    "cocaine": ['Cocaïne', 'Cocaine', 'Coke'],
    "XTC": ['XTC', 'ecstasy'],
    "GHB": ['GHB', 'gamma-hydroxyboterzuur', '4-hydroxybutaanzuur']
}


a = '''CREATE TABLE IF NOT EXISTS public.court_verdicts (
        case_id varchar(100) NOT NULL,
        case_text text,
        PRIMARY KEY (case_id)
    )'''

b = '''CREATE TABLE IF NOT EXISTS public.case_data (
        case_id varchar(100) NOT NULL,
        titel varchar(255),
        court_datum date,
        uitspraak_type varchar(30),
        gerechtelijk_product_type varchar(30),
        procedure_soort varchar(100),
        rechtsgebieden varchar(100),
        PRIMARY KEY (case_id)
    )'''

c = '''CREATE TABLE IF NOT EXISTS public.sewer (
        year integer,
        cocaine numeric,
        amphetamine numeric,
        MDMA numeric,
        methamphetamine numeric
    )'''


d = '''CREATE TABLE IF NOT EXISTS public.drug_prevalence_count (
        case_id varchar(100) NOT NULL,
        court_datum date, 
        safrol integer,
        piperonal integer,
        PMK integer,
        BMK integer,
        apaan integer,
        GBL integer, 
        MDP2P integer,
        efedrine integer, 
        ergotamine integer,
        lyserginezuur integer,
        methamphetamine integer,
        MDMA integer,
        amphetamine integer,
        cocaine integer,
        XTC integer,
        GHB integer,
        PRIMARY KEY (case_id)
    )'''

queries = [a, b, c, d]