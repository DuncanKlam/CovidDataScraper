# Covid Data Scraper (Shell Tool) (in Python)
 
## How to Use:
1. Prereqs: Python3

1. Download the most recent release of this file (v.1.0.0 as of 4/7/2022)

1. Open your shell tool (I enjoy Powershell) and navigate to the folder the file is located

1. >python scrapeCovidData.py

It's that simple! A spinner will pop up until the scraper stops scraping (it's a lot of data), and will display the last seven days of covid data about Delaware County, Indiana. 

## Custom Queries
This shell tool supports custom queries through the use of tags! There are 7 tags associated with this shell tool:
<ul>
<li>-r: Date Range Size</li>
<li>-o: Date Range Origin</li>
<li>-c: County Name</li>
<li>-s: State Name</li>
<li>-S: State Data Retrieval after County Data Retrieval</li>
<li>-SO: State Data Retrieval only</li>
<li>--help: Displays the function helper</li>
</ul>

They can be mixed and matched to your heart's content. See what kind of crazy queries you can make!

### Custom Date Range
The date range is changed with the -r tag:
> python scrapeCovidData.py -r 10
will display a result that spans ten days

### Custom Date Range Origin (more on this: About Range Origin)
The date range origin can be changed with the -o tag:
> python scrapeCovidData.py -o '2022,3,20'
will display a result starting from March 20, 2022
It is imperative that you structure the origin string this way 'YYYY,M,D'
The above notation requests you include no leading zeroes '2022,03,20' would be an invalid argument

### Custom County 
The county about which to fetch data can be changed with the -c tag:
> python scrapeCovidData.py -c 'Wayne'
will display a result for Wayne County, Indiana

### Custom State 
The state about which to fetch data can be changed with the -s tag:
> python scrapeCovidData.py -s 'Michigan'
will display a result for Delaware County, Michigan
Since this place doesn't exist, you often have to use -s in conjunction with -c
Try this:
> python scrapeCovidData.py -c 'Wayne'
then:
> python scrapeCovidData.py -c 'Wayne' -s 'Michigan'

### State Data As Well
The overall state data can be retrieved after the county data by setting the -S tag:
>python scrapeCovidData.py -S
will display a result for Indiana State, US after displaying a result for Delaware County, Indiana
This can be used in conjunction with -s to get info about other states

### State Data Only
The overall state data will only be retrieved, no county data will:
>python scrapeCovidData.py -SO
will display a result for Indiana State, US

#### About Range Origin (and some other stuff):
The scraper builds a list of dates to inject into http queries. The dates are calculated by starting at the origin date (defaults to yesterday, because the current days data hasn't been collected) and stepping backwards one day at a time, n times. n is defined by the optional -r tag's argument; if not provided it defaults to 7. 

## Closing Thoughts:
This started as a simple web scraping exercise in Python. What it turned into is a perhaps a pre-optimized overworked shell tool project but it is semi-useful so I'm counting it as a success.
This script scrapes a repository on Github, maintained by Johns Hopkins University. The repo contains daily total cases, which is split into deaths, recovered, and active cases. Unfortunately, nobody is really recording recovered or active cases anymore, so we glean what we can from active cases and deaths.
I know you could achieve the same effect with a script that either installs this repository or updates it and parses the files within, but that's not what I wanted to practice. (but hey, fun project idea) As well, it doesn't have much error handling for http requests or much else, so it's pretty easy to break. Also not really the point, but of note. The thing that could use some work is the search function, I'm sure just doing a linear search isn't the fastest. It may also just be the http response time that is the bottleneck, in which case, meh. What are ya gonna do. This is a fun project that I will continue to work on and hopefully relase a few versions of.(though I don't know what more I'm gonna do, really) Ultimately I really just hope other people find this useful, maybe not as a shell tool in itself, but at least as a learning exercise in writing a basic web scraper made difficult by an ADD addled programmer who only kind of knows python, but has a passion for functional programming. 

