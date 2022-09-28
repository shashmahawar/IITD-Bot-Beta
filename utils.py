import csv, datetime, json, requests
from bs4 import BeautifulSoup

# Global Variables

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
