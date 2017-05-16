import gradr

gbook = gradr.Gradebook()
gbook.importNames('names.csv')
gradr.processGradescope('gradescope.csv', 'exam.csv', list(gbook.table.keys()))
