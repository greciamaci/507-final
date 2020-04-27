from bs4 import BeautifulSoup
import requests
import csv
import json
import sqlite3
import pandas as pd

CACHE_FILENAME = "cache.json"
CACHE_DICT = {}
BASEURL = "https://dataomaha.com"


#creation of first table csv
original_url = 'https://dataomaha.com/school-ratings/district/omaha-public-schools'
school_table = pd.read_html(original_url)
basic_info = school_table[0]
basic_info.columns = ['Schools', 'Type', 'Rating']
indexNames = basic_info[ (basic_info['Schools'] == "Norris Middle School") | (basic_info["Schools"] == "Lewis & Clark Middle School") ].index
basic_info.drop(indexNames , inplace=True)
basic_info.to_csv("basicinfo.csv")


class Performance: 
    def __init__(self, student_success="No Score", transitions = "No Score", ed_opportunities = "No Score", career_readiness="No Score", assessment="No Score", educator_effectiveness="No Score"):
        self.student_success = student_success
        self.transitions = transitions
        self.ed_opportunities = ed_opportunities
        self.career_readiness = career_readiness
        self.assessment = assessment
        self.educator_effectiveness = educator_effectiveness

    def info(self):
        insert_list = []
        insert_list.append(self.student_success)
        insert_list.append(self.transitions)
        insert_list.append(self.ed_opportunities)
        insert_list.append(self.career_readiness)
        insert_list.append(self.assessment)
        insert_list.append(self.educator_effectiveness)
        return insert_list

def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the dictionary.

    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None

    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict
CACHE_DICT = open_cache()

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key


def get_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    response = requests.get(baseurl, params=params)
    return response.text


def make_request_with_cache(baseurl, param={}):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    
    request_key = construct_unique_key(baseurl, param)
    if request_key in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[request_key]
    else:
        print("Fetching")
        CACHE_DICT[request_key] = get_request(baseurl, param)
        save_cache(CACHE_DICT)
        return CACHE_DICT[request_key]

base = "https://dataomaha.com"
url = 'https://dataomaha.com/school-ratings/district/omaha-public-schools'
request = make_request_with_cache(url)
soup = BeautifulSoup(request, 'html.parser')
search_div = soup.find("table", class_="table")

#INFORMATION
info_list = search_div.find_all("tr")
#URLs
info = {}
for school in info_list:
    key = school.find("a").text.lower()
    x = school.find("a").attrs['href']
    info[key] = base + x

#The following have to be deleted because the pages don't work (the actual pages have a server error)
del info["lewis & clark middle school"]
del info["norris middle school"]

#Accessing csv file
file_contents = open('basicinfo.csv', 'r')
file_reader = csv.reader(file_contents)
next(file_reader) # skip header row


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    #soup information
    request = requests.get(site_url)
    content = request.content
    soup = BeautifulSoup(content, 'html.parser')
    box = soup.find_all("table", class_="table")
    table = box[1]
    list_of_lists = []

    for things in table.find_all("tr"): 
        list_of_lists.append(things.find_all("td"))

    #student_success 
    student_success = float((list_of_lists[0][1]).string)

    #transitions
    transitions = float((list_of_lists[1][1]).string)
    

    #ed_opportunities
    ed_opportunities = float((list_of_lists[2][1]).string)

    #career_readiness
    career_readiness = float((list_of_lists[2][3]).string)

    #assessment
    assessment = float((list_of_lists[4][1]).string)

    #educator_effectiveness
    educator_effectiveness = float((list_of_lists[5][1]).string)

    return Performance(student_success, transitions, ed_opportunities, career_readiness, assessment, educator_effectiveness)

all_info = []

#Appending instances to a list 
for k,v in info.items():
    instance = get_site_instance(v)
    matrix = Performance.info(instance)
    all_info.append(tuple(matrix))
    

#DATABASE
def create_db():
    conn = sqlite3.connect('final.sqlite')
    cur = conn.cursor()

    drop_basic_info = '''
    DROP TABLE IF EXISTS "Basic_Info";
    '''
    
    create_basic_sql = '''
        CREATE TABLE IF NOT EXISTS "Basic_Info" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
            "School" TEXT NOT NULL,
            "Level" TEXT NOT NULL, 
            "Rating" REAL NOT NULL
        )
    '''

    drop_performance = '''
    DROP TABLE IF EXISTS "Performance";
    '''

    create_performance_sql = '''
        CREATE TABLE IF NOT EXISTS "Performance"(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Student_Success' REAL NOT NULL,
            'Transitions' REAL NOT NULL,
            'Ed_Opportunities' REAL NOT NULL,
            'Career_Readiness' REAL NOT NULL,
            'Assessment' REAL NOT NULL,
            'Educator_Effectiveness' REAL NOT NULL,
            'School_Id' INTEGER,
            FOREIGN KEY ("School_Id") REFERENCES "Basic_Info"("Id")
        )
    '''

    insert_basic_info = '''
        INSERT INTO Basic_Info
        VALUES (NULL,?,?,?)
    '''


    insert_performance = '''
        INSERT INTO Performance 
        VALUES (NULL,?,?,?,?,?,?,?)
    '''

    insert_sid = '''
        SELECT Id
        FROM Basic_Info
    '''
    

    
    cur.execute(drop_basic_info)
    cur.execute(create_basic_sql)
    cur.execute(drop_performance)
    cur.execute(create_performance_sql)

    for row in file_reader:
        cur.execute(insert_basic_info, row[1:])

    cur.execute(insert_sid) 
    res = cur.fetchall()
    
    for obs, b in zip(all_info, res):
        cur.execute(insert_performance, [obs[0],obs[1],obs[2],obs[3],obs[4],obs[5],b[0]])

        

    conn.commit()
    conn.close()
create_db()



