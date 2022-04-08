#!/bin/bash

import sys
import requests
import re
import math
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta
from halo import Halo


##Some Constants and Things##
isCountyDataRequested = True
isStateDataRequested = False
r = 7
c = "Delaware"
s = "Indiana"
o = date.today() - timedelta(days=1)
URL_BASE = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/"
args_help = "ARGS: *-r *-c *-s *-o *-S, *-SO"
optional_help = "*- ::Denotes optional tag::"
day_num_help = "-r int ::Date Range::Date range of size n, starting from origin to n days back::Default==7::example -r 9::"
county_help = "-c str ::County Name::Name of county to obtain data about::Default=='Delaware'::example -c 'Wayne'::"
state_help = "-s str ::State Name::Name of state to obtain data about::Default=='Indiana'::example -s 'Michigan'::"
origin_help = "-o str ::Origin Date::Date to begin ranging back from::Default is yesterday's date::example -o '2022,3,17'::"
state_data_also_help = "-S ::State Data Retrieval Also::Adds state data retrieval after county data retrieval::Default==False"
state_data_only_help = "-SO ::State Data Retrieval Only::Changes data retrieval from county to state::Default==False"
error_message = "\n{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n".format(optional_help,day_num_help,county_help,state_help,origin_help,state_data_also_help,state_data_only_help)


##Utility Methods, Builder/Retreival/Calculators##
def build_url(date):
    return "{0}{1}-{2}-{3}.csv".format(URL_BASE,date[1],date[2],date[0])

def build_date_list(numOfDays, origin):
    dates = []
    for i in range(numOfDays):
        pastDate = origin - timedelta(days=(i))
        dates.append(str(pastDate).split("-"))
    dates.reverse()
    return dates
 
def get_count(index,array):
    return array[index].get("count")
   
def get_date(index,array):
    return array[index].get("date")
    
def get_confirmed(index, array):
    return array[index].get("confirmed")

def calculate_count_total(array):
    totalConfirmed = 0
    totalDead = 0
    for item in array:
        totalConfirmed += item.get("confirmed")
        totalDead += item.get("deaths")
    return totalConfirmed, totalDead

def trunc(number, decimalPlace):
    factor = 10.0 ** decimalPlace
    return math.trunc(number * factor) / factor

##Print Statements##
def whitespace_():
    print("\n\n")

def improper_response_(tag,arg,reason):
    sys.exit("\tERROR===========================\n\tIMPROPER INPUT: {0} -> {1}\n\tREASON: {0} {2}".format(tag,arg,reason))

def display_location_information_(specificLoc,specificLocType,generalLoc):
    print("\t{0} {1}, {2}\n".format(specificLoc,specificLocType,generalLoc))

def display_covid_data_(formerDate,recentDate,formerCount,recentCount,formerConfirmed,recentConfirmed,formerDead,recentDead,dayRange):
    print("\tTotal cases as of {1}: {0}".format(recentConfirmed,recentDate))
    print("\tTotal deaths (confirmed + probable) as of {1}: {0}".format(recentDead,recentDate))
    #print("\tTotal active/recovered cases as of {1}: {0}".format(recentConfirmed-recentDead,recentDate))
    print("\tCase Growth over {0} day(s) ({2}-{3}): {1}".format(dayRange,recentConfirmed-formerConfirmed,formerDate,recentDate))
    print("\tDeath Growth over {0} day(s) ({2}-{3}): {1}".format(dayRange,recentDead-formerDead,formerDate,recentDate))
    #print("\tActive/Recovered Growth over {0} day(s) ({2}-{3}): {1}".format(dayRange,(recentConfirmed-formerConfirmed)-(recentDead-formerDead),formerDate,recentDate))
    #print("\t{0} Day Case Avg: {1}".format(dayRange,trunc((recentConfirmed-formerConfirmed)/dayRange,2)))
    print("\t{0} Day Death Avg: {1}".format(dayRange,trunc((recentDead-formerDead)/dayRange,2)))
    print("\t{0} Day Active/Recovered Case Avg: {1}".format(dayRange,trunc(((recentConfirmed-formerConfirmed)-(recentDead-formerDead))/dayRange,2)))


##Logic Checks##
def is_date_range_incorrect(arg):
    if(arg.isnumeric()):
        if(int(arg) < 1):
            return True
        else:
            return False
    else:
        return True

def is_previous_arg_valid_tag(arg):
    if arg == "-c" or arg == "-r" or arg == "-s" or arg == "-o":
        return True
    else:
        return False

def is_tag_last_in_array_(i,array):
    if(i+1 == len(array)): #Check if tag is last argument in argv
        improper_response_(array[i],"","has no value")

##Query Conditions##
def county_query_condition(county, state):
    return (lambda entry : entry[2] == state and entry[1] == county)
        
def state_query_condition(state):
    return (lambda entry : entry[2] == state)

##HTML Procesing##
def get_case_count(url, condition):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find('div', class_="js-blob-code-container").find_all(class_="blob-code-inner")
    result = []
    for i in results:
        entry = i.contents[0].split(",")
        if(condition(entry)):
            result.append({
            'confirmed' : int(entry[7]),
            'deaths' : int(entry[8])
            })
    return result

##The Heavy Lifting##
def scrape_data(dayRange,condition, dateList):
    caseCount = []
    spinner = Halo(text='Loading', spinner="dots", color='red')
    spinner.start()
    for i in dateList:
        dailyNumbers = get_case_count(build_url(i),condition)
        caseCount.append({
            "date" : "{0}/{1}".format(i[1],i[2]),
            "count" : dailyNumbers
            })
    spinner.stop()
    return caseCount

def scrape_processor_(dayRange, rangeOrigin, condition, locationInfo):
    dateList = build_date_list(dayRange, rangeOrigin)
    
    caseCount = scrape_data(dayRange,condition, dateList)
    
    recentCount = get_count(dayRange-1,caseCount)
    recentDate = get_date(dayRange-1, caseCount)
    formerCount = get_count(0,caseCount)
    formerDate = get_date(0,caseCount)
    
    recentConfirmed, recentDead = calculate_count_total(recentCount)
    formerConfirmed, formerDead = calculate_count_total(formerCount)
    
    whitespace_()
    display_location_information_(locationInfo[0],locationInfo[1],locationInfo[2])
    display_covid_data_(formerDate,recentDate,formerCount,recentCount,formerConfirmed,recentConfirmed,formerDead,recentDead,dayRange)
    whitespace_()



 
######CLI Arguments Processing#######
for i in range(len(sys.argv)):
    if (i != 0):
        if (sys.argv[1] == "--help"):
            sys.exit("\n{1}\n{0}".format(error_message,args_help)) #display help message
        if (sys.argv[i] == "-r"): #range tag
            is_tag_last_in_array_(i, sys.argv)
            newRange = sys.argv[i+1]
            if(is_date_range_incorrect(newRange)):
                improper_response_("-r",sys.argv[i+1],"is either zero, negative, or a string")
            else:
                r = int(newRange)
        elif (sys.argv[i] == "-c"): #county tag
            is_tag_last_in_array_(i, sys.argv)
            newCounty = sys.argv[i+1]
            if(newCounty.isnumeric()):
                improper_response_("-c",sys.argv[i+1],"is a number")
            else:
                c = newCounty
        elif (sys.argv[i] == "-s"): #state tag
            is_tag_last_in_array_(i, sys.argv)
            newState = sys.argv[i+1]
            if(newState.isnumeric()):
                improper_response_("-s",sys.argv[i+1],"is a number")
            else:
                s = newState
        elif (sys.argv[i] == "-o"): #origin tag
            is_tag_last_in_array_(i, sys.argv)
            newOrigin = sys.argv[i+1]
            if(newOrigin.isnumeric()):
                improper_response_("-o",sys.argv[i+1],"is incorrect")
            else:
                l = newOrigin.split(",")
                o = date(int(l[0]),int(l[1]),int(l[2]))
        elif (sys.argv[i] == "-S"): #State Data Also tag
            isStateDataRequested = True;
        elif (sys.argv[i] == "-SO"): #State Data Only tag
            isCountyDataRequested = False;
            isStateDataRequested = True;
        else:   
            if (not is_previous_arg_valid_tag(sys.argv[i-1])):
                improper_response_(sys.argv[i],"","is not a valid tag")

######Driver Code#######
if(isCountyDataRequested):
    scrape_processor_(r, o, county_query_condition(c,s), [c, "County", s])
if(isStateDataRequested):
    scrape_processor_(r, o, state_query_condition(s), [s, "State", "US"])

