import csv, datetime, json, requests
from bs4 import BeautifulSoup

# Global Variables
kerberos = {}
branches = []
hostels = []
course_slots = {}
courseinfo = {}
slots = []
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
    
    global course_slots
    course_slots = {}
    with open("datafiles/Courses_Offered.csv", "r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            course_slots[row[1].split('-')[-1]] = row[3]
    
    global slots
    slots = []
    with open("datafiles/slot_timings.json", "r") as f:
        slots = json.load(f)
    
    global courseinfo
    courseinfo = {}
    with open("datafiles/raw_course_data_2.xml") as cdata:
        s = "".join(cdata.readlines())
        tree = BeautifulSoup(s, 'html.parser')

    global majors
    majors = {}
    with open("datafiles/Majors.json", "r") as f:
        majors = json.load(f)

    # handling missing courses as well: 
    mscidx = 0
    for dep in tree.findAll("courses"):
        for course in dep.findAll("course"):
            ccode = getattr(course.find("code"), "string", None)
            if not ccode:
                ccode = f"MISS{mscidx}"
                mscidx += 1

            courseinfo[ccode] = {
                "code": ccode,
                "name": getattr(course.find("name"), "string", None),
                "credits": getattr(course.find("credits"), "string", None),
                "credit-structure": getattr(course.find("credit-structure"), "string", None),
                "pre-requisites": getattr(course.find("pre-requisites"), "string", None),
                "overlap": getattr(course.find("overlap"), "string", None),
                "department": dep.get("department"),
                "description": getattr(course.find("description"), "string", None)
            }


def get_courses(kerberos):
    with open("datafiles/course_lists.json", "r") as f:
        course_lists = json.load(f)
    courses = []
    for course in course_lists:
        if kerberos in course_lists[course]:
            if course.startswith('2302'):
                courses.append(course.split('-')[-1])
    return courses

def get_course_count(code):
    code = "2302-" + code.upper()
    with open("datafiles/course_lists.json", "r") as f:
        course_lists = json.load(f)
    if code not in course_lists:
        return 0
    return len(course_lists[code])

async def fetch_ldap(msg):
    url = "http://ldapweb.iitd.ac.in/LDAP/courses/gpaliases.html"
    response = requests.get(url, verify=False)

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
        url = f"http://ldapweb.iitd.ac.in/LDAP/courses/{course['href']}"
        response = requests.get(url, verify=False)
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

    with open(f"datafiles/course_lists_{datetime.datetime.utcnow().strftime('%d_%m_%Y')}.json", "w") as outfile:
        json.dump(courseLists, outfile)

    await msg.edit(content=f"Fetched LDAP!")

def course_info(code):
    code = code.upper()
    if code not in courseinfo:
        return None
    course = courseinfo[code]
    dependencies = []
    for c in courseinfo:
        if code in str(courseinfo[c]['pre-requisites']):
            dependencies.append(c)
    if dependencies == []: dependencies = [None]
    course['dependencies'] = dependencies
    return course

def get_majors(kerberos):
    courses = get_courses(kerberos)
    major_list = []
    for course in courses:
        course = course[:6]
        if course in majors:
            major_details = majors[course]
            major_details['Course'] = course
            major_list.append(major_details)
    major_list = sorted(major_list, key=lambda x: (x['Day'], x['Time']))
    return major_list

reload()