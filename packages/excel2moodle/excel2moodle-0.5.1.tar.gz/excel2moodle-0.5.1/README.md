# excel 2 Moodle
![Logo](excel2moodleLogo.png "Logo excel2moodle"){width=35%}

This Python program helps to create Moodle questions in less time.
The idea is to write the questions data into a spreadsheet file, from which the program generates the moodle compliant xml Files. 
All questions or a selection of questions can be exported into one xml file to be imported into moodle.

## Concept
The concept is, to store the different questions into categories of similar types and difficulties of questions, for each of which, a separated sheet in the Spreadsheet document should be created.

A `settings` sheet contains global settings to be used for all questions and categories.
Another sheet stores metadata for the different categories of questions.
And each category lives inside a separate sheet inside the spreadsheet document. 

## Getting Started

### Installation
To get started with excel2moodle first have a look at the [installation](https://jbosse3.gitlab.io/excel2moodle/howto.html#excel2moodle-unter-windows-installieren)
If you already have python and uv installed, it is as easy as running `uv tool install excel2moodle`.

### [ Documentation ](https://jbosse3.gitlab.io/excel2moodle/index.html)
Once excel2moodle is installed you can checkout the [example question sheet](https://gitlab.com/jbosse3/excel2moodle/-/tree/master/example?ref_type=heads) 
in the repository.

Some steps are already documented as [ tutorials ](https://jbosse3.gitlab.io/excel2moodle/howto.html)
you can follow along.

And please have a look into the [**user Reference**](https://jbosse3.gitlab.io/excel2moodle/userReference.html)
of the documentation. 
That part explains each part of defining a question.


## Functionality
* Equation Verification:
    + this tool helps you to validate the correct equation for the parametrized Questions.
* Question Preview:
    + This helps you when selecting the correct questions for the export.
* Export Options:
    + you can export the questions preserving the categories in moodle

### Question Types
* Generate multiple Choice Questions:
    + The answers can be pictures or normal text
* Generate Numeric Questions
* Generate parametrized numeric Questions
* Generate parametrized cloze Questions


![MainWindow](mainWindow.png "Logo excel2moodle"){width=80%}

## Licensing and authorship
excel2moodle is lincensed under the latest [GNU GPL license](https://gitlab.com/jbosse3/excel2moodle/-/blob/master/LICENSE)
Initial development was made by Richard Lorenz, and later taken over by Jakob Bosse

## Supporting
A special thanks goes to the [Civil Engineering Departement of the Fachhochschule Potsdam](https://www.fh-potsdam.de/en/study-further-education/departments/civil-engineering-department) 
where i was employed as a student associate to work on this project.

If You want to support my work as well, you can by me a [coffee](https://ko-fi.com/jbosse3)

# Changelogs

## 0.5.1 (2025-06-24)
Minor docs improvement and question variant bugfix

### bugfix (1 change)

- [Bullet points variant didn't get updated](https://gitlab.com/jbosse3/excel2moodle/-/commit/7b4ad9e9c8a4216167ae019859ebaa8def81d57f)

## 0.5.0 (2025-06-20)
settings handling improved

### feature (2 changes)

- [Pixmaps and vector graphics scaled to fit in preview](https://gitlab.com/jbosse3/excel2moodle/-/commit/00a6ef13fb2a0046d7641e24af6cf6f08642390e)
- [feature: category Settings implemented](https://gitlab.com/jbosse3/excel2moodle/-/commit/d673cc3f5ba06051aa37bc17a3ef0161121cb730)

### improvement (1 change)

- [Tolerance is harmonized by questionData.get()](https://gitlab.com/jbosse3/excel2moodle/-/commit/8d1724f4877e1584cc531b6b3f278bdea68b5831)

### Settings Errors are logged (1 change)

- [Log Errors in settings Sheet](https://gitlab.com/jbosse3/excel2moodle/-/commit/07e58f957c69ea818db1c5679cf89e287817ced3)

