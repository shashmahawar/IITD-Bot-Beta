import csv, datetime, json, requests
from bs4 import BeautifulSoup

# Global Variables
kerberos = {}
branches = []
hostels = []
days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
meals = ['breakfast', 'lunch', 'snacks', 'dinner']
years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022']

def reload():
    global kerberos
    kerberos = {}
    with open("datafiles/kerberos.csv", "r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            kerberos[row[0]] = {"name": row[1], "hostel": row[2]}

    global branches
    branches = []
    with open("datafiles/branches.csv", "r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            branches.append(row[0])

    global hostels
    hostels = []
    with open("datafiles/hostels.csv", "r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            hostels.append(row[0])

    

async def fetch_ldap(msg):

    url = "http://ldap1.iitd.ernet.in/LDAP/courses/gpaliases.html"
    response = requests.get(url)

    if response.status_code != 200:
        await msg.edit(content="Error: Could not fetch LDAP Data. Host not connected to network!")
        return
    
    soup = BeautifulSoup(response.text,'html.parser')
    courses = soup.find_all('a')
    courseLists = {}
    i = 100/len(courses)
    k = 0

    for course in courses:
        print(course)
        url = f"http://ldap1.iitd.ernet.in/LDAP/courses/{course['href']}"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        students = soup.find_all('td', attrs = {'align' : 'LEFT'})
        sList = []
        for s in students:
            sList.append(s.text)
        courseLists[course.text] = sList
        if k == 5:
            await msg.edit(content=f"_Fetching LDAP Data:_ **{round(i,2)}%**")
            k = 0
        i += 100/len(courses)
        k += 1
    
    with open("datafiles/course_lists.json", "w") as outfile:
        json.dump(courseLists, outfile)

    with open(f"datafiles/course_lists_{datetime.datetime.now().strftime('%d_%m_%Y')}.json", "w") as outfile:
        json.dump(courseLists, outfile)

    await msg.edit(content=f"Fetched LDAP!")

reload()