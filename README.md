# gradr

This is a script for processing CSV grade spreadsheets into letter grades.
The original use was to automate the process of turning (cleaned) speadsheets of raw homework and quiz, etc. scores into letter grades, in the context of a large lecture with multiple TAs (or "GSIs" if you're from Berkeley.)

In general a "score" is a numerical thing and a "grade" is a string like A+, but sometimes we call A+ 13, A 12, etc.

Leaving off the "e" is trendy so I have complied.

## Documentation
gradr.py defines a "Gradebook" object that stores student names and ids and a dictionary of scores/grades.
It has a bunch of methods for importing names and scores, combining scores together, and exporting reports.
It should be pretty clear if you look at the code.
There is also an example in the folder Example: running script.py will generate a grade report.


## Formatting

There are three types of input CSV files that gradr accepts:

Names files are just a list of names and student IDs.
* The first column contains the names
* The second column contains the student IDs (which can be any string but are usually numbers)

Assignment gradesheet files record a list of scores on individual assignments, along with the max points possible and the name of the assignment type.
They are intended for *one* type of assignment: one file for quizzes, one for homework, etc.
* The first row has a blank entry, the name of the assignment type, then numbers giving the maximum points for each assignment
  * Assignment types/names need to be unique! They will be used as dict keys
* Below the first row:
  * The first column has student IDs
  * The second column has the number of assignments to drop (this can vary between students because of excused absences, etc.)
  * The remaining columns have individual assignment scores

Exam gradesheet files record exam scores
They are intended to hold *all* the exam scores at once, and they are what processGradescope produces
* The first row has a blank entry and then a list of exam names
  * Assignment types/names need to be unique! They will be used as dict keys
* Below the first row:
  * The first column has studen IDs
  * The remaining columns have the exam score
