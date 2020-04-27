import sqlite3
import plotly.graph_objs as go


def gather_level_rank(id):
    connection = sqlite3.connect("final.sqlite")
    c = connection.cursor()
    data = []
    # Code below from Sxribe: https://stackoverflow.com/questions/59664705/selecting-an-id-which-matches-a-user-input-in-sqlite3-python
    for row in c.execute("SELECT School FROM Basic_Info WHERE Id=?", (id, )):
        data.append(row)
    for stype in c.execute("SELECT Level FROM Basic_Info WHERE Id=?", (id, )):
        data.append(stype)
    for rank in c.execute("SELECT Rating FROM Basic_Info WHERE Id=?", (id, )):
        data.append(rank)
    print('Information for:',''.join(data[0]),"\n")
    print('School Type:',''.join(data[1]),"\n")
    print('Overall Nebraska Department of Education Peformance Score:',''.join(data[2]), "\n")


def graph(id):

    connection = sqlite3.connect("final.sqlite")
    c = connection.cursor()
    data = []
    name = []

    for one in c.execute("SELECT Student_Success FROM Performance WHERE Id=?", (id, )):
        data.append(one)
    for two in c.execute("SELECT Transitions FROM Performance WHERE Id=?", (id, )):
        data.append(two)
    for three in c.execute("SELECT Ed_Opportunities FROM Performance WHERE Id=?", (id, )):
        data.append(three)
    for four in c.execute("SELECT Career_Readiness FROM Performance WHERE Id=?", (id, )):
        data.append(four)
    for five in c.execute("SELECT Assessment FROM Performance WHERE Id=?", (id, )):
        data.append(five)
    for six in c.execute("SELECT Educator_Effectiveness FROM Performance WHERE Id=?", (id, )):
        data.append(six)
    for names in c.execute("SELECT School FROM Basic_Info WHERE Id=?", (id, )):
        name.append(names)

    numbers = []

    for o in data:
        numbers.append(o[0])
    
    xvals = ['Positive Partnerships Relationships and Student Success', 'Transitions', 'Educational Opportunities and Access', 'College and Career Readiness', 'Assessment', 'Educator Effectiveness']
    yvals = numbers
    
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title=f"Breakdown of 2015 Performance Scores for {name[0][0]}. (*Note: each performance category score ranges from 0 to 3*)")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    fig.show()
    

def levels():
    connection = sqlite3.connect("final.sqlite")
    c = connection.cursor()
    countlev = []
    for levels in c.execute("SELECT Level, COUNT(*) FROM Basic_Info GROUP BY Level ORDER BY (CASE Level WHEN 'Elementary School'THEN 1 WHEN 'Middle School' THEN 2 WHEN 'High School' THEN 3 END) ASC"):
        countlev.append(levels)
    
    nums = []
    for i in countlev:
        nums.append(i[1])

    xvals = ["Elementary Schools", "Middle Schools", "High Schools"]
    yvals = nums
    
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title=f"Number of Omaha Public Schools by Type (2015)")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    fig.show()


def rankings():
    connection = sqlite3.connect("final.sqlite")
    c = connection.cursor()
    countlev = []
    # source sql code for sorting by clause from https://www.designcise.com/web/tutorial/how-to-custom-sort-in-sql-order-by-clause
    for levels in c.execute("SELECT Rating, COUNT(*) FROM Basic_Info GROUP BY Rating ORDER BY (CASE Rating WHEN 'Needs Improvement'THEN 1 WHEN 'Good' THEN 2 WHEN 'Great' THEN 3 WHEN 'Excellent' THEN 4 END) ASC"):
        countlev.append(levels)
    
    nums = []
    for i in countlev:
        nums.append(i[1])

    xvals = ["Needs Improvement", "Good", "Great", "Excellent"]
    yvals = nums
    
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title=f"Overall Omaha Public Schools Ratings (2015)")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    fig.show()


def averages():
    connection = sqlite3.connect("final.sqlite")
    c = connection.cursor()
    countlev = []

    for levels in c.execute("SELECT ROUND(AVG(Student_Success),1), ROUND(AVG(Transitions),1), ROUND(AVG(Ed_Opportunities),1), ROUND(AVG(Career_Readiness),1), ROUND(AVG(Assessment),1), ROUND(AVG(Educator_Effectiveness),1) FROM Performance"):
        countlev.append(levels)
    
    for i in countlev:
        numeros = i

    xvals = ['Positive Partnerships Relationships and Student Success', 'Transitions', 'Educational Opportunities and Access', 'College and Career Readiness', 'Assessment', 'Educator Effectiveness']
    yvals = numeros
    
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title=f"Overall Omaha Public Schools Performance Score Breakdown Averages (2015)")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    fig.show()


def prints():
    print("___________________________________________________________________________","\n")
    print('What would you like to do?',"\n")
    print('1) Examine the number of types of schools')
    print('2) Examine the rating counts')
    print('3) Examine score averages for each performance category')
    print('4) Return to Main Menu')
    print('5) Quit Program')
    


if __name__ == "__main__":
    
    while True:
        connection = sqlite3.connect("final.sqlite")
        cursor = connection.cursor()
        query = "SELECT School FROM Basic_Info"
        result = cursor.execute(query).fetchall()
        connection.close()
        count = 0
        print("\n")
        print("The following is a list of Omaha Public Schools")
        print("___________________________________________________________________________","\n")
        for schools in result:
            count += 1
            print(count,''.join(schools), "\n")
        print("___________________________________________________________________________")
        prompt_one = input("Enter a Number to Learn More About an Omaha Public School, enter 'summary' for more options, or enter 'exit' to quit: ")
        print("___________________________________________________________________________","\n")
        if prompt_one == "exit":
            break
        else:
            if prompt_one.isnumeric():
                if int(prompt_one) > 84:
                    print("Invalid input. Enter a valid number or 'summary'.")
                elif int(prompt_one) <= 0:
                    print("Sorry that number is out of range, try again")
                elif 0 < int(prompt_one) <= 84:
                    gather_level_rank(prompt_one)

                    while True:
                        print("___________________________________________________________________________")
                        more_options = input("To see a breakdown of the performance score, enter 'graph'; enter 'back' to select another school or 'exit' to quit: ")
                        if more_options.lower() == 'exit':
                            quit()
                        elif more_options.lower() == 'back':
                            break
                        elif more_options.lower() == 'graph':
                            graph(prompt_one)
                        else:
                            print("Invalid input, try again.")
                else:
                    continue
            elif prompt_one.lower().isalpha():
                if prompt_one.lower() == 'summary':
                    prints()                    
                    while True:
                        print("___________________________________________________________________________")
                        prompt_three = input("Enter a number to select a summary option about Omaha Public Schools: ")
                        if prompt_three.isnumeric():
                            if int(prompt_three) == 1:
                                levels()
                                prints()
                            elif int(prompt_three) == 2:
                                rankings()
                                prints()
                            elif int(prompt_three) == 3:
                                averages()
                                prints()
                            elif int(prompt_three) == 4:
                                break
                            elif int(prompt_three) == 5:
                                quit()
                            else:
                                print('Invalid input')
                        else:
                            print('Invalid input, enter a valid number.')

                else:
                    print("Invalid input. Enter a valid number or 'summary'.")
            else:
                print("Invalid input. Enter a valid number or 'summary'.")
