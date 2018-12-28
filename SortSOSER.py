from tkinter import filedialog
from tkinter import *
import csv
import random
import math
import os

#Used for calculating closest state
closest_state = {
"AK": ["WA"],
"AL": ["MS","TN","GA","FL"],
"AR": ["MO","TN","MS","LA","TX","OK"],
"AZ": ["CA","NV","UT","CO","NM"],
"CA": ["OR","NV","AZ"],
"CO": ["WY","NE","KS","OK","NM","AZ","UT"],
"CT": ["NY","MA","RI"],
"DC": ["MD","VA"],
"DE": ["MD","PA","NJ"],
"FL": ["AL","GA"],
"GA": ["FL","AL","TN","NC","SC"],
"HI": ["CA"],
"IA": ["MN","WI","IL","MO","NE","SD"],
"ID": ["MT","WY","UT","NV","OR","WA"],
"IL": ["IN","KY","MO","IA","WI"],
"IN": ["MI","OH","KY","IL"],
"KS": ["NE","MO","OK","CO"],
"KY": ["IN","OH","WV","VA","TN","MO","IL"],
"LA": ["TX","AR","MS"],
"MA": ["RI","CT","NY","NH","VT"],
"MD": ["VA","WV","PA","DC","DE"],
"ME": ["NH"],
"MI": ["WI","IN","OH"],
"MN": ["WI","IA","SD","ND"],
"MO": ["IA","IL","KY","TN","AR","OK","KS","NE"],
"MS": ["LA","AR","TN","AL"],
"MT": ["ND","SD","WY","ID"],
"NC": ["VA","TN","GA","SC"],
"ND": ["MN","SD","MT"],
"NE": ["SD","IA","MO","KS","CO","WY"],
"NH": ["VT","ME","MA"],
"NJ": ["DE","PA","NY"],
"NM": ["AZ","UT","CO","OK","TX"],
"NV": ["ID","UT","AZ","CA","OR"],
"NY": ["NJ","PA","VT","MA","CT"],
"OH": ["PA","WV","KY","IN","MI"],
"OK": ["KS","MO","AR","TX","NM","CO"],
"OR": ["CA","NV","ID","WA"],
"PA": ["NY","NJ","DE","MD","WV","OH"],
"RI": ["CT","MA"],
"SC": ["GA","NC"],
"SD": ["ND","MN","IA","NE","WY","MT"],
"TN": ["KY","VA","NC","GA","AL","MS","AR","MO"],
"TX": ["NM","OK","AR","LA"],
"UT": ["ID","WY","CO","NM","AZ","NV"],
"VA": ["NC","TN","KY","WV","MD","DC"],
"VT": ["NY","NH","MA"],
"WA": ["ID","OR"],
"WI": ["MI","MN","IA","IL"],
"WV": ["OH","PA","MD","VA","KY"],
"WY": ["MT","SD","NE","CO","UT","ID"]
}

#Creates a list for SOSers from the SOSer csv file
def flock_leader(flock_leader_file):
    leader_list = {}
    flock_counter = 0
    with open(str(flock_leader_file), "rt") as sosers:
        soserslist = csv.reader(sosers)
        next(soserslist)
        for item in soserslist:
            if item[4] == "":
                break
            flock_counter += 1
            leader_list[flock_counter] = [item[5], item[4]]
        #print(leader_list)
    return leader_list, len(leader_list)

#Breadth First Search algorithm that determines a list of closest states
def closeness(graph, start):
    explored = []
    queue = [start]
 
    while queue:
        node = queue.pop(0)
        if node not in explored:
            explored.append(node)
            neighbours = graph[node]
            for neighbour in neighbours:
                queue.append(neighbour)

    explored.pop(0)
    return explored

#Writes to a csv file 
def write_to_csv(flock_list):
    with open("output.csv", "wt") as write_file:
        writer = csv.writer(write_file)
        for flock in flock_list:
            for person in flock:
                writer.writerow(person)
    return 0

#Counts all the genders 
def count_gender(flock_list):
    num_of_males = 0
    num_of_females = 0
    nonbinary = 0
    for person in flock_list:
        if person[9].lower() == "male":
            num_of_males += 1
        elif person[9].lower() == "female":
            num_of_females += 1
        else:
            nonbinary += 1

    print("Males: ", num_of_males,"Females: ", num_of_females, "Nonbinary: ", nonbinary)
    return num_of_males

#Check if students from a marginalized community to placed into a flock that already has too many 
#students from marginalized identities. Purpose is to make sure all flocks have somewhat of an even
#distribution of marginalized students
def check_max(flock_list, max_val, flock_tot, curr_flock):
    new_flock = curr_flock
    for i in range(flock_tot):
        if len(flock_list[new_flock]) >= (max_val//2):
            new_flock = (curr_flock + i) % flock_tot
        else:
            return new_flock
    return new_flock

#Check if white students being placed in flocks that are not full. 
def check_max_state(flock_list, max_val, flock_tot, curr_flock):
    new_flock = curr_flock
    min_flock_list = flock_list[curr_flock]
    max_flock_list = flock_list[curr_flock]

    for i in range(flock_tot):
        if len(flock_list[new_flock]) >= (max_val-1):
            new_flock = (curr_flock + i) % flock_tot
        else:
            return new_flock

#Sort students into flocks depending on which state they're from 
def sorting_state(sort_flock, flock_leads, flock_num, max_num, stu_list):
    sorted_flocks = sort_flock
    state_dict = {}
    sorted_leaders = []

    for item in stu_list:
        if item[11] in state_dict:
            state_dict[item[11]].append(item)
        else:
            state_dict[item[11]] = [item]

    state_dict = sorted(state_dict.items(), key = lambda x: (len(x[1])))

    for k,v in state_dict:
        for leader in flock_leads:
            if flock_leads[leader][0] == k:
                sorted_leaders.insert(0,leader)
            else:
                sorted_leaders.insert(len(sorted_leaders),leader)
        target_states = closeness(closest_state,k)

        base_assign = sorted_leaders[0] - 1
        while len(v) > 0:
            curr_length = len(v)
            i = check_max_state(sorted_flocks, max_num, flock_num, base_assign)
            if curr_length % 2 != 0 and curr_length >= 3:
                for n in range(3):
                    sorted_flocks[i].append(v[0])
                    del v[0]
                    base_assign = (base_assign + 1) % len(flock_leads)
            elif curr_length % 2 == 0 and curr_length >= 2:
                for n in range(2):
                    sorted_flocks[i].append(v[0])
                    del v[0]
                    base_assign = (base_assign + 1) % len(flock_leads)
            else:
                for state in target_states:
                    for soser in sorted_leaders:
                        if state == flock_leads[soser][0]:
                            sorted_flocks[soser-1].append(v[0])
                            break
                    break
                del v[0]
                base_assign = (base_assign + 1) % len(flock_leads)

        sorted_leaders = []
        
    return sorted_flocks    

def sorting(sort_flock, flock_num, max_num, stu_list):
    sorted_flocks = sort_flock
    random_flock_assign = random.randrange(0,flock_num,1)
    while(len(stu_list) > 0):
        curr_length = len(stu_list)
        assign_flock_num = check_max(sorted_flocks, max_num, flock_num, random_flock_assign)
        if curr_length % 2 != 0 and curr_length >= 3:
            for n in range(3):
                sorted_flocks[assign_flock_num].append(stu_list[0])
                del stu_list[0]
                random_flock_assign = (random_flock_assign + 1) % flock_num
        elif curr_length % 2 == 0 and curr_length >= 2:
            for n in range(2):
                sorted_flocks[assign_flock_num].append(stu_list[0])
                del stu_list[0]
                random_flock_assign = (random_flock_assign + 1) % flock_num                
        else:
            sorted_flocks[assign_flock_num].append(stu_list[0])
            del stu_list[0]
            random_flock_assign = (random_flock_assign + 1) % flock_num

    return sorted_flocks

def printing_format(flist):
    flock_num = 1
    for i in range(len(flist)):
        print ("flock: ", flock_num)
        print ("--------------------------------------")
        count_gender(flist[i])
        print ("--------------------------------------")
        for data in flist[i]:
            data[5] = i+1
            print(data[3] + ", " + data[4], "|" , data[9], "|", data[11], "|" ,data[10])
        flock_num += 1
        print('\n')

def main():
    flock_leaders, flock_num = flock_leader("soserlist.csv")
    #session_num = int(input("enter the session number: "))
    session_num = int(userEnter.get())
    filename = "writeflock.csv"
    flocks = []
    for i in range(flock_num):
        flocks.append([])

    states = []
    pacific_islander = []
    hispanic = []
    white = []
    asian = []
    african_american = []
    american_indian_alaska = []
    count = 0

    with open(filename, "rt") as speadsheet:
        reader = csv.reader(speadsheet)
        next(reader)
        for row in reader:
            count += 1
            if row[11] not in states:
                states.append(row[11])
            if row[19].lower() == "yes":
                white.append(row)
            elif row[14].lower() != "no":
                american_indian_alaska.append(row)
            elif row[16].lower() != "no":
                african_american.append(row)
            elif row[17].lower() != "no":
                hispanic.append(row)
            elif row[18].lower() != "no":
                pacific_islander.append(row)
            elif row[15].lower() != "no":
                asian.append(row)
    
    speadsheet.close()

    len_pacific_islander = len(pacific_islander)
    len_hispanic = len(hispanic)
    len_white = len(white)
    len_asian = len(asian)
    len_african_american = len(african_american)
    len_american_indian_alaska = len(american_indian_alaska)

    max_flock = math.ceil(count/flock_num)
    white = sorted(white, key=lambda x:x[12])
    
    random.shuffle(pacific_islander)
    random.shuffle(hispanic)
    random.shuffle(asian)
    random.shuffle(african_american)
    random.shuffle(american_indian_alaska)
    random.shuffle(white)

    
    sorting(flocks, flock_num, max_flock, asian)
    sorting(flocks,flock_num,max_flock, pacific_islander)
    sorting(flocks, flock_num, max_flock, hispanic)
    sorting(flocks, flock_num, max_flock, african_american)
    sorting(flocks, flock_num, max_flock, american_indian_alaska)

    #sorting(flocks, flock_num, max_flock, white)
    sorting_state(flocks, flock_leaders, flock_num, max_flock, white)
    printing_format(flocks)

    print("Pacific Islander: ", len_pacific_islander)
    print("Hispanic: ", len_hispanic)
    print("White: ", len_white)
    print("Asian: ", len_asian)
    print("African American: ", len_african_american)
    print("American Indian/Alaska: ", len_american_indian_alaska)
    print("States: ", states)

    print("total students: ", count)
    print("max flock size: ", math.ceil(count/flock_num))
    #write_to_csv(flocks)

def browseStudent():
    filename = filedialog.askopenfilename(title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
    StudentFile = filename

def browseSOSER():
    filename = filedialog.askopenfilename(title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
    SOSERFile = filename

#main()

root = Tk()
uploadStudentButton = Button(text="Upload Students", command=browseStudent)
uploardSOSERButton = Button(text="Uploard SOSERs", command=browseSOSER)
sessionLabel = Label(root, text="Enter Session Number")
userEnter = Entry(root)
generateButton = Button(text="Generate", command="testFile")

uploadStudentButton.pack()
uploardSOSERButton.pack()
sessionLabel.pack()
userEnter.pack()
generateButton.pack()
root.mainloop()
