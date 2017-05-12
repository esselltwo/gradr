#See README.md for documentation, data formatting, etc.

import csv

#Constants
#Names and numerical values of the grades that can be assigned
GradeNames = ['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
GradeNumbers = [0,2,3,4,5,6,7,8,9,10,11,12,13]

def parseScores(scores):
    #Converts list of strings to floats, treating empty strings as 0.0
    output = []
    for a in scores:
        if a == '':
            output.append(float(0))
        else:
            output.append(float(a))
    return output

def processGradescope(infileName, outfileName, examName, idList):
    #Takes a Gradescope CSV infile and extracts the scores on examName
    #for just the students in idList.
    #Writes to outfile in the standard gradr assignment sheet format
    #This method assumes max points are the same for every student

    with open(infileName) as infile, open(outfileName,'w') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile, lineterminator = '\n')

        #generate header
        firstRow = reader.__next__()
        scoreIndex = firstRow.index(examName)
        maxScoreIndex = scoreIndex + 1
        idIndex = 1
        maxScore = reader.__next__()[maxScoreIndex]
        writer.writerow(['', examName, maxScore])
        infile.seek(1) #go back to second row

        #extract grades
        for row in reader:
            for id in idList:
                if id == row[idIndex]: writer.writerow([id,0,row[scoreIndex]])

class Gradebook:
    #Tracks grading rules, students, and scores

    def __init__(self):
        #gradeCategories should be a list of category names
        #ex ['Homework', 'Quiz', 'Total Section']
        #or ['Section', 'Midterm', 'Final', 'Total']
        #these will be used as dict keys, so they need to be unique
        self.gradeCategories = []

        #table is a dict with keys student IDs and values dicts of scores
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
            firstRow = True
            for row in nameReader:
                self.table[row[1]] = {}
                self.names[row[1]] = row[0]

    def importScaledScore(self, filename):
        #This method computes scaled scores (including drops)
        #for each student and adds them to the gradebook
        #Intended for things like dropping lowest N quizzes and averaging remainder

        #filename is a CSV file with individual assignment scores
        #first column is student ids (with first row blank)
        #second column is number of assignments to drop (with first row category name)
        #remaining columns are assignments (with first row max points)

        with open(filename) as file:
            scoreReader = csv.reader(file)

            firstRow = True
            for row in scoreReader :
                if firstRow: #Extract the first row to get the max possible points
                    category = row[1] #second column has category name
                    self.gradeCategories.append(category)
                    maxScores = parseScores(row[2:]) #first two columns are blank
                    firstRow = False
                else:
                    scores = parseScores(row[2:])
                    scaledScores = []
                    for maxScore, score in zip(maxScores,scores):
                        scaledScores.append(score/maxScore)
                    scaledScores.sort()
                    toDrop = int(row[1])
                    scaledScores = scaledScores[toDrop:] #drop lowest toDrop scores
                    average = sum(scaledScores)/float(len(scaledScores))
                    self.table[row[0]][category] = average

    def foldCategories(self, toFold, weights, newCat, delOld = False):
        #Folds list toFold of grade categories together
        #Folds according to weight vector weights
        #New category has name newCat
        #If delOld = True, delete old category names

        for id in self.table:
            total = 0
            for cat, wt in zip(toFold, weights):
                total = total + self.table[id][cat]*wt
                if delOld: del self.table[id][cat]
            self.table[id][newCat] = total

    def applyCuttoffs(self, sourceCat, targetCat, cutoffs, labels):
        #Uses the numerical cutoffs to assign labels
        #Numerical cutoffs are checked against sourceCat
        #Labels are applied to targetCat

        for id in self.table:
            for bound, label in zip(cutoffs, labels):
                if self.table[id][sourceCat] > bound: self.table[id][targetCat] = label

    def exportGradeReport(self, cats, filename):
        #Writes a grade report spreadsheet to filename
        #Names, ids, and the categories in cats are included

        with open(filename, 'w') as file:
            outwriter = csv.writer(file, lineterminator = '\n')
            outwriter.writerow(['Name', 'ID'] + cats) #print header
            for id in self.table:
                row = [self.names[id], id]
                for c in cats: row.append(str(self.table[id][c]))
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
