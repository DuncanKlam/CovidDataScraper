#!/usr/bin/python

import sys
import requests
import re
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta
from halo import Halo

##Some Constants and Things##
isCountyDataRequested = True
r = 7
c = "Delaware"
s = "Indiana"
URL_BASE = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/"
args_help = "ARGS: *-r *-c *-s *-S"
optional_help = "*- ::Denotes optional tag::"
day_num_help = "-r ::Date Range::(ex. -r 7)::Date range of size n, starting from yesterday to n days back::Default==7::"
county_help = "-c ::County Name::(ex. -c 'Delaware')::Name of county to obtain data about::Default=='Delaware'::"
state_help = "-s ::State Name::(ex. -s 'Indiana')::Name of state to obtain data about::Default=='Indiana'::\n   --If set without -S, likely will have to set -c"
state_data_help = "-S ::State Data Retrieval::Changes data retrieval method to whole state::"
error_message = "\n{0}\n{1}\n{2}\n{3}\n{4}\n".format(optional_help,day_num_help,county_help,state_help,state_data_help)

##Utility Methods, Builder/Retreival##
def build_url(date):
    return "{0}{1}-{2}-{3}.csv".format(URL_BASE,date[1],date[2],date[0])

def build_date_list(num_of_days):
    dates = []
    today = date.today()
    for i in range(num_of_days):
        past_date = today - timedelta(days=(i+1))
        dates.append(str(past_date).split("-"))
    dates.reverse()
    return dates
    
def get_count(index,array):
    return array[index].get("count")
   
def get_date(index,array):
    return array[index].get("date")

##Print Statements##
def whitespace():
    print("\n\n")

def improper_response(arg,tag,reason):
    sys.exit("\tERROR===========================\n\tIMPROPER INPUT: {0} -> {1}\n\tREASON: {0} {2}".format(tag,arg,reason))

def display_location_information(specificLoc,specificLocType,generalLoc):
    print("\t{0} {1}, {2}\n".format(specificLoc,specificLocType,generalLoc))

def display_covid_data(firstDate,lastDate,lastValue,dayRange, caseDiff):
    print("\tTotal cases as of {1}: {0}".format(lastValue,lastDate))
    print("\tCase Growth over {0} day(s) ({2}-{3}): {1}".format(dayRange,caseDiff,firstDate,lastDate))
    print("\t{0} Day Avg: {1}".format(dayRange,caseDiff/dayRange))

##Logic Checks##
def date_range_is_incorrect(arg):
    if(arg.isnumeric()):
        if(int(arg) < 1):
            return True
        else:
            return False
    else:
        return True

def previous_arg_is_valid_tag(arg):
    if arg == "-c" or arg == "-r" or arg == "-s":
        return True
    else:
        return False

def is_tag_last_in_array(i,array):
    if(i+1 == len(array)): #Check if tag is last argument in argv
        improper_response("",array[i],"has no value")

##The Heavy Lifting##
def get_case_count(url, condition):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find('div', class_="js-blob-code-container").find_all(class_="blob-code-inner")
    result = []
    for i in results:
        entry = i.contents[0].split(",")
        if(condition(entry)):
            result.append(int(entry[7]))
    return result

def scrape_data(dayRange,condition):
    caseCount = []
    spinner = Halo(text='Loading', spinner="dots", color='red')
    spinner.start()
    date_list = build_date_list(dayRange)
    for i in range(dayRange):
        date = date_list[i]
        dailyNumbers = get_case_count(build_url(date),condition)
        caseCount.append({
            "date" : "{0}/{1}".format(date[1],date[2]),
            "count" : dailyNumbers
            })
    spinner.stop()
    return caseCount

##Different Query Methods##
def scrape_county_data(county, state, dayRange):
    end = dayRange-1
    condition = (lambda entry : entry[2] == state and entry[1] == county)
    caseCount = scrape_data(dayRange,condition)
    caseDiff = get_count(end,caseCount)[0] - get_count(0,caseCount)[0]
    
    whitespace()
    display_location_information(county, "County", state)
    display_covid_data(get_date(0,caseCount),get_date(end, caseCount),get_count(end, caseCount)[0], dayRange, caseDiff)
    whitespace()

def scrape_state_data(state, dayRange):
    end = dayRange-1
    condition = (lambda entry : entry[2] == state)
    caseCount = scrape_data(dayRange,condition)
    
    yesterdayTotalConfirmed = 0
    for num in get_count(end,caseCount):
        yesterdayTotalConfirmed += num
    
    firstdayTotalConfirmed = 0
    for num in get_count(0,caseCount):
        firstdayTotalConfirmed += num
        
    caseDiff = yesterdayTotalConfirmed - firstdayTotalConfirmed
    
    whitespace()
    display_location_information(state, "State", "US")
    display_covid_data(get_date(0,caseCount),get_date(end, caseCount),yesterdayTotalConfirmed, dayRange, caseDiff)
    whitespace()
    
######Driver Code#######
for i in range(len(sys.argv)):
    if (i != 0):
        if (sys.argv[1] == "--help"):
            sys.exit("\n{1}\n{0}".format(error_message,args_help)) #display help message
        if (sys.argv[i] == "-r"): #range tag
            is_tag_last_in_array(i, sys.argv)
            newRange = sys.argv[i+1]
            if(date_range_is_incorrect(newRange)):
                improper_response(sys.argv[i+1],"-r","is either zero, negative, or a string")
            else:
                r = int(newRange)
        elif (sys.argv[i] == "-c"): #county tag
            is_tag_last_in_array(i, sys.argv)
            newCounty = sys.argv[i+1]
            if(newCounty.isnumeric()):
                improper_response(sys.argv[i+1],"-c","is a number")
            else:
                c = newCounty
        elif (sys.argv[i] == "-s"): #state tag
            is_tag_last_in_array(i, sys.argv)
            newState = sys.argv[i+1]
            if(newState.isnumeric()):
                improper_response(sys.argv[i+1],"-s","is a number")
            else:
                s = newState
        elif (sys.argv[i] == "-S"): #State Data tag
            isCountyDataRequested = False;
        else:   
            if (not previous_arg_is_valid_tag(sys.argv[i-1])):
                improper_response("",sys.argv[i],"is not a valid tag")

if(isCountyDataRequested):
    scrape_county_data(c,s,r)
else:
    scrape_state_data(s,r)