# gradr

This is a script for processing CSV grade spreadsheets into letter grades.
The original use was to automate the process of turning (cleaned) speadsheets of raw homework and quiz, etc. scores into letter grades, in the context of a large lecture with multiple TAs (or "GSIs" if you're from Berkeley.)

Leaving off the "e" is trendy so I have complied.

## Formatting

The input should be a collection of CSV files (that work with the csv package in Python, because apparently the format is ill-defined.)
The intention is that one sheet represents one type of assignment: quizzes, homework, midterms, etc.
Those sheets are in turn prepared from some sort of master grading sheet; in my case, that sheet is exported from bCourses or some similar web portal.

* The first column should contains names or some other identifying string.
  * The first row of the first column should be blank
* The second column lists how many quiz or homework scores to drop
  * This can vary between students because of excused absences.
  * The first row of the second column should also be blank
* The remaining columns give information on the assignments.
  * The first row gives the maximum number of points possible on the assignment for normalization purposes
  * The remaining rows give each students' points earned
