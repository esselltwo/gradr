#See README.md for documentation, data formatting, etc.

import csv

#Data is kept in a dictionary
#keys are student names and the values are lists of scores

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

def initGradeDict(filename):
    #Initializes the dictionary of grades with names
    with open(filename, newline='') as f:
        nameReader = csv.reader(f)
        grades = {}

        firstRow = True
        for row in nameReader:
            if firstRow: #first row doesn't have names
                firstRow = False
            else:
                grades[row[0]] = []

        return grades

def calcSubScore(grades, filename):
    #Given a csv with one type of assignment (quiz, HW, etc.)
    #this finds a scaled score (out of 1) and appends to the dict entry
    with open(filename, newline='') as gradefile:
        gradeReader = csv.reader(gradefile)

        firstRow = True
        for row in gradeReader:
            if firstRow: #Extract the first row to get the max possible points
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
                grades[row[0]].append(sum(scaledScores)/float(len(scaledScores)))
    return(grades)

def calcScore(grades, weights):
    #Takes weighted sum of each student's subscores and appends
    for id in grades:
        total = 0
        for score, weight in zip(grades[id],weights):
            total = total + score * weight
        grades[id].append(total)

    return grades

def extractList(grades):
    #Extracts a list of grades to look at in Mathematica
    #Format for Mathematica lists is {x1, x2, ...}
    output = '{'
    for id in grades:
        output = output + str(grades[id][-1]) + ', '
    return output[:-2] + '}' #there's an extra terminal ', ' that we drop

def assignGrade(score, cutoffs, type):
    #Given numerical cutoffs, assigns a grade to a given score

    #type is either 'names' or 'numbers'
    if type == 'letter':
        labels = GradeNames
    elif type == 'number':
        labels = GradeNumbers

    #Cutoffs are a list:
    #Everyone with a score above cutoffs[0] gets at least an F,
    #everyone with a score above cutoffs[1] gets at least a D-, etc.
    for bound, label in zip(cutoffs,labels):
        if score > bound: grade = label

    return grade

def exportGrades(grades, cutoffs, filename):
    #Takes a dict of grades and prints a formatted CSV to filename
    with open(filename, 'w') as f:
        outwriter = csv.writer(f, lineterminator = '\n')
        for student in grades:
            letter = assignGrade(grades[student][-1], cutoffs,'letter')
            number = str(assignGrade(grades[student][-1], cutoffs, 'number'))
            row = [student] + [str(n) for n in grades[student]] + [letter] + [number]
            outwriter.writerow(row)
