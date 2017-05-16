import gradr


sectionCutoffs = [-float('inf'), float('inf'), .35, .40, .43, .48, .58, .68, .74, .79, .86, .91, .98]
mid1Cutoffs = [-float('inf'), float('inf'), 14, 20, 24, 29, 32, 34, 36, 43, 46, 48, 51]
mid2Cutoffs = [-float('inf'), float('inf'), 16, 20, 24, 30, 34, 36, 40, 45, 47, 51, 55]
#D- isn't a grade we use, except sometimes
examCutoffs = [-float('inf'), 20, 25, 30, 33, 40, 46, 49, 53, 58, 65, 73, 80]

letterCutoffs = [-float('inf'), 6, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62]

gbook = gradr.Gradebook()

gbook.importNames('names.csv')
gbook.importScaledScores('quiz.csv')
gbook.importScaledScores('homework.csv')
gbook.foldCategories(['Homework', 'Quiz'], [.5,.5], 'Section')
gbook.assignGrades('Section', sectionCutoffs)
gbook.importScores('exam.csv')
gbook.assignGrades('First Midterm', mid1Cutoffs)
gbook.assignGrades('Second Midterm', mid2Cutoffs)
gbook.assignGrades('Final Exam', examCutoffs)


sect = 'Section'
mid1 = 'First Midterm'
mid2 = 'Second Midterm'
final = 'Final Exam'
for id in gbook.table:
    grades = gbook.gradeTable[id]
    if grades[final].is_missing():
        total = 0 #failing grade
    elif grades[mid1].is_missing():
        if grades[mid2].is_missing():
            total = 0 #failing grade
        else:
            total = grades[sect].getValue() + 2*grades[mid1].getValue() + 2*grades[final].getValue()
    elif grades[mid2].is_missing():
        total = grades[sect].getValue() + grades[mid1].getValue() + 3*grades[final].getValue()
    else:
        total = grades[sect].getValue() + grades[mid1].getValue() + grades[mid2].getValue() + 2*grades[final].getValue()

    gbook.table[id]['Total'] = gradr.Score(total)

gbook.assignGrades('Total', letterCutoffs)

gbook.exportGradeReport(['Homework',  'Quiz', 'Section', 'First Midterm', 'Second Midterm', 'Final Exam', 'Total'], 'out.csv')
gbook.exportCalCentral('Total', 'upload.csv')
