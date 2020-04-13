# Russian-Memo
An application to memorize russian words built with django.
in this application teachers can create tests and see the scores of the students.
Students can answer tests, create cards and memorize them using the supermemo2 algorithm (a space repetition algorithm).
Students can also play games like the hangman. 

## Getting Started

```
git clone https://github.com/ilyasEzz/Russian-Memo.git

cd Russian-Memo

python -m venv venv

### in a Bash  Command Shell
source venv/Scripts/activate

### in Windows Command Shell :
venv/Scripts\activate.bat

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic

python manage.py runserver
```
Opem localhost:8000
