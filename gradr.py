#See README.md for documentation, data formatting, etc.

import csv

#Constants
#Grades are internally represented as integers:
#0  2   3   4   5   6   7   8   9   10  11  12  13
#F  D-  D   D+  C-  C   C+  B-  B   B+  A-  A   A+
Grades = [0,2,3,4,5,6,7,8,9,10,11,12,13]
LetterGrades = {0 : 'F', 2 : 'D-',3 : 'D',4:  'D+',5: 'C-',6: 'C',7: 'C+',8: 'B-',9: 'B',10: 'B+',11: 'A-',12: 'A',13: 'A+'}

def processGradescope(infileName, outfileName, idList):
    #Takes a Gradescope CSV infile and extracts the exam scores
    #for just the students in idList.
    #Writes to outfile in the format used for importScores

    with open(infileName) as infile, open(outfileName,'w') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile, lineterminator = '\n')

        #find assignment names
        firstRow = reader.__next__()
        #Gradescope uses format
        #name, SID, email, exam 1 score, max exam 1 score, exam 2 score, max exam 2 score, ...
        numExams = int((len(firstRow) -3)/2)
        examColumns = [3 + 2*k for k in range(numExams)]
        examNames = [firstRow[i] for i in examColumns]

        #print header
        writer.writerow(['']+ examNames)

        #extract grades
        idIndex = 1 #we assume we're using SID numbers, which are in column 2
        for row in reader:
            for id in idList:
                if id == row[idIndex]:
                    writer.writerow([id] + [row[i] for i in examColumns])

class Score:
    #An object for containing numerical scores on assignments
    #Basically just a float, but can also take value ''
    #if missing assigments need to be treated differently than zero

    def __init__(self, score):
        if score == '':
            self.score = ''
        else:
            self.score = float(score)

    #Returns True if the assignment score is missing
    def missingQ(self):
        if self.score == '':
            return True
        else:
            return False

    #Yields the numerical value of a score treating missing as zero
    def getValue(self):
        if self.missingQ():
            return 0.0
        else:
            return self.score

def scaleAndDrop(scores, maxScores, toDrop):
    #Takes a list of Score objects scores,
    #a list maxScores of maximum scores as floats,
    #and an integer number of assignments to drop
    #and returns the list of scaled scores

    output = [score.getValue()/maxScore for score, maxScore in zip(scores, maxScores)]
    output.sort()
    return output[toDrop:]

class Gradebook:
    #Tracks grading rules, students, and scores

    def __init__(self):
        #gradeCategories should be a list of category names
        #ex ['Homework', 'Quiz', 'Total Section']
        #or ['Section', 'Midterm', 'Final', 'Total']
        #these will be used as dict keys, so they need to be unique
        self.gradeCategories = []

        #table is a dict with keys student IDs and values dicts of Scores
        #the lists of grades should correspond to categories
        self.table = {}

        #names is a dict with keys student IDs and values student names
        self.names = {}

        # #grades is a dict with keys student IDs and values final letter grades
        # self.grades = {}

    def importNames(self, filename):
        #Takes a CSV file with names and student IDs and initializes
        #the table and name dicts with appropriate data

        with open(filename) as file:
        #filename should be a CSV with the first column names and the second IDs
        #other columns will be ignored
            nameReader = csv.reader(file)
            for row in nameReader:
                self.table[row[1]] = {}
                self.names[row[1]] = row[0]

    def importScores(self, filename):
        #This method imports scores from a file
        #These scores are not scaled or processed
        #Typical use is a CSV with all the exam scores

        #filename is a CSV file with assignment names and scores
        #first column is student IDs with first row blank
        #remaining columns have header the assignment name
        #and rows each student's score

        with open(filename) as file:
            scoreReader = csv.reader(file)

            #extract header
            firstRow = scoreReader.__next__()
            cats = firstRow[1:]
            self.gradeCategories = self.gradeCategories + cats

            for row in scoreReader:
                scores = [Score(x) for x in row[1:]]
                for score, cat in zip(scores, cats):
                    self.table[row[0]][cat] = score


    def importScaledScores(self, filename):
        #This method computes scores (including drops and possibly scaling)
        #for each student and adds them to the gradebook
        #Intended for things like dropping lowest N quizzes and averaging remainder

        #filename is a CSV file with individual assignment scores
        #first column is student ids (with first row blank)
        #second column is number of assignments to drop (with first row category name)
        #remaining columns are assignments (with first row max points)

        with open(filename) as file:
            scoreReader = csv.reader(file)

            #extract header
            firstRow = scoreReader.__next__()
            category = firstRow[1] #second column has category name
            self.gradeCategories.append(category)
            maxScores = [float(x) for x in firstRow[2:]] #first two columns are blank
            #These are not Score objects because they should never be blank

            for row in scoreReader:
                scores = [Score(x) for x in row[2:]]
                toDrop = int(row[1])
                scaledScores = scaleAndDrop(scores, maxScores, toDrop)
                average = sum(scaledScores)/float(len(scaledScores))
                self.table[row[0]][category] = Score(average)

    def foldCategories(self, toFold, weights, newCat, delOld = False):
        #Folds list toFold of grade categories together
        #Folds according to weight vector weights
        #New category has name newCat
        #If delOld = True, delete old category names

        for id in self.table:
            total = 0
            for cat, wt in zip(toFold, weights):
                total = total + self.table[id][cat].getValue()*wt
                if delOld: del self.table[id][cat]
            self.table[id][newCat] = Score(total)

    def applyCuttoffs(self, sourceCat, targetCat, cutoffs, labels):
        #Uses the numerical cutoffs to assign labels
        #Numerical cutoffs are checked against sourceCat
        #Labels are applied to targetCat
        #If sourceCat and targetCat are the same, this replaces the values

        for id in self.table:
            if self.table[id][sourceCat].missingQ():
                newValue = Score('')
            else:
                for bound, label in zip(cutoffs, labels):
                    if self.table[id][sourceCat].getValue() > bound: newValue = label
            self.table[id][targetCat] = newValue
            del newValue #this should not continue between loops

    def exportGradeReport(self, cats, filename, letterCats = []):
        #Writes a grade report spreadsheet to filename
        #Names, ids, and the categories in cats are included
        #Categories in letterCats are treated as letter grades
        #and printed as letters, not numbers

        with open(filename, 'w') as file:
            outwriter = csv.writer(file, lineterminator = '\n')

            #generate and print header
            catHeader = []
            for c in cats:
                catHeader.append(c)
                if c in letterCats: catHeader.append('')
            outwriter.writerow(['Name', 'ID'] + catHeader)

            for id in self.table:
                row = [self.names[id], id]
                for c in cats:
                    x = self.table[id][c]
                    if type(x) == type(0): #if it's a letter grade
                        if c in letterCats:
                            row.append(LetterGrades[x])
                        else:
                            row.append(str(x))
                    elif type(x) == type(Score('')):
                        if x.missingQ():
                            row.append('')
                        else:
                            row.append(str(x.score))
                outwriter.writerow(row)

    def exportCalCentral(self, cat, filename):
        #Writes a spreadsheet for uploading to CalCentral
        #The format is Student ID number in column A and letter grade in column C
        #cat is the label of the grade categoy containing final letter grades

        with open(filename, 'w') as file:
            outwriter = csv.writer(file, lineterminator = '\n')
            for id in self.table:
                outwriter.writerow([id, '', self.table[id][cat]])

    def mathematicaList(self, cat):
        #Returns a list of scores to analyze externally
        #Formatted as a string that Mathematica will interpret as a list
        output = '{'
        for id in self.table: output = output + str(self.table[id][cat]) + ', '
        return output[:-2] + '}' #there's an extra terminal ', ' that we drop
