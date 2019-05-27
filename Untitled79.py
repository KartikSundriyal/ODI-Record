
# coding: utf-8

# In[17]:


import urllib
import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm

def make_soup(url):
    thepage = urllib.request.urlopen(url)
    soupdata = BeautifulSoup(thepage,"html.parser")
    return soupdata


URL = "http://stats.espncricinfo.com/ci/engine/stats/index.html?class=2;spanmin1=05+Jan+1870;spanval1=span;template=results;type=batting"

current_page_soup = make_soup(URL)

def get_names_on_current_page(current_page_soup):
    name = []
    for record in current_page_soup.find_all("tr",attrs={'data1'}):
        for a in record.find("td"):
            for n in record.find("a"):
                name.append(n)
    names = name[::2]
    return names

def next_page_links(current_page_soup):
    name = []
    stored_next_page_links = ""
    for r in current_page_soup.findAll("tr",attrs={"data2"}):
        for n in r.findAll("a"): 
            stored_next_page_links = stored_next_page_links + "," + (n.get("href"))
            
    stored_next_page_links2 = stored_next_page_links.split(",")
    return stored_next_page_links2[3]
    
def player_link(current_page_soup , player):
    nextlink = current_page_soup.find("div", id="engine-dd"+ str(player))
    storedlinks = ""
    for i in nextlink.findAll("li"):
        for j in i.findAll("a"):
            storedlinks = storedlinks + "," + (j.get("href"))
    storedlinks2 = storedlinks.split(",")
    return storedlinks2[-3]

def total_pages(current_page_soup):
    total_page_find = ''
    for r in current_page_soup.findAll("tbody"):
        for i in r.findNext("tr",attrs="data2"):
            for j in i.findAllNext("b"):
                total_page_find = total_page_find + "," + j.contents[0]
    pages = int(total_page_find.split(",")[2])
    return pages

def total_players(current_page_soup):
    total_player_find = ''
    for r in current_page_soup.findAll("tbody"):
        for i in r.findNext("tr",attrs="data2"):
            for j in i.findAllNext("b"):
                total_player_find = total_player_find + "," + j.contents[0]
    players = int(total_player_find.split(",")[5])
    return players

def runs_scored(player_page_suop):
    mruns = []
    cmrun = ''
    for recordruns in player_page_suop.findAll("tr",attrs={'data1'}):
        for a in recordruns.find("td"):
            if(cmrun == ""):
                cmrun = str(a)
            else:
                cmrun = cmrun + "," +str(a)
    cmrun = cmrun.replace("*","")
    mruns.append(cmrun.split(","))
    mruns = mruns[0][2:]
        
    mruns2 = []                                    
    for i in range(len(mruns)):
        try:
            mruns2.append(int(mruns[i]))
        except:
            mruns2.append(mruns[i])

    return mruns2                                       # List of runs scored in each innings     

def years_scored(player_page_suop):
    yearstr = ''
    for recordruns in player_page_suop.findAll("tr",attrs={'data1'}):
        for a in recordruns.findAll("b"):
            if(yearstr == ""):
                yearstr = a.contents[0]
            else:
                yearstr = yearstr + "," + a.contents[0]
                    
    yearlst = []
    yearlst.append(yearstr.split(","))
        
    year_list = []             
    for i in range(len(yearlst[0])):
        year_list.append(int(yearlst[0][i][-4:]))
    return year_list                                    # List of all the years in which the player played   


def run_year_dictionary(mruns2,year_list):
    inruns = []
    run_year_dic = {}
        
    j  = year_list[0]
    k = j
    for i in range(len(mruns2)):
        j  = year_list[i]
        if(k==j):
            inruns.append(mruns2[i])
            continue
        else:
            run_year_dic[year_list[i-1]]  = inruns
            k = j
            inruns = []
            inruns.append(mruns2[i])
            run_year_dic[year_list[i]]  = inruns
    return run_year_dic                          # A dictionary containing Runs as values and years as keys      
    
counter = 0
final_list = []

for page in tqdm(range(1,total_pages(current_page_soup)+1)):
    if (page == 1):
        current_page_soup = make_soup(URL)
    else:
        current_page_soup = make_soup("http://stats.espncricinfo.com" + next_page_links(current_page_soup))
    
    for player in range(1,51):
        player_page_soup = make_soup("http://stats.espncricinfo.com" + player_link(current_page_soup,player))
        
        mruns2 = runs_scored(player_page_soup)
        
        year_list = years_scored(player_page_soup)
        
        inruns = []
        run_year_dic = {}
        
        run_year_dic = run_year_dictionary(mruns2,year_list)
                
        final_player_dic = {}         # A dictionary containing years as keys and a list of Runs(In that year) & Aggregate Runs as Values 
        final_run_list = []
        agg_runs = 0
        year_wise_runs = 0
        
        inning_run=0
        final_player_dic = {}
        final_run_list = []
        agg_runs = 0
        year_wise_runs = 0
        for i in run_year_dic.keys():
            for inning_run in run_year_dic[i]:
                try:
                    year_wise_runs = year_wise_runs + inning_run
                except:
                    year_wise_runs = year_wise_runs + 0
            final_run_list.append(year_wise_runs)
            agg_runs = agg_runs + year_wise_runs
            final_run_list.append(agg_runs)
            year_wise_runs=0
            final_player_dic[i] = final_run_list
            final_run_list = []
        
        name_list = get_names_on_current_page(current_page_soup)
        
        new_list = []
        new_list = [name_list[player-1] , final_player_dic]
        final_list.append(new_list)
        
        counter = counter + 1
    if(counter>total_players(current_page_soup)):
        break


# In[86]:


name_list = []
for i in range(len(final_list)):
    name_list.append(final_list[i][0])
d = {}
d["Names/Year"] = name_list
l = []
#nl = []
for j in tqdm(range(1870,2020)):
    for i in range(len(name_list)):
        if (j) in final_list[i][1].keys():
            l.append(final_list[i][1][j])
   
        else:
            l.append(0)
    d[str(j)] = l
    l=[]
    
df = pd.DataFrame
df = pd.DataFrame(d)

df.to_csv("Result.csv", encoding='utf-8', index=False)    

