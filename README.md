# DB Lab 2

## 1. Team
Gasser ibrahim shalaby  2304106  readme,frontend,Css
Seif El-Din Amr Abd El-Fattah 2304205 backend,database

## 2. Technology
- **Back end:** Python 3 + Flask, PyMySQL, bcrypt, python-dotenv
- **Front end:** HTML/CSS/JavaScript
- **Database:** MySQL, database `registration`

## 3. How to run (from an empty machine)
1. Install Python 3.10+, MySQL Server and Git.
2. Clone the repo and enter it: `git clone <url> && cd <folder>`
open VS code then click on file select open folder and select folder db-lab2
3. Create the environment and install packages:
select terminal => new terminal then
   ```
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  #if error happened use it 
   pip install -r requirements.txt
   ```
4. Build the database: `mysql -u root -p (put your password) database/schema.sql`
5. Copy `.env.example` to `.env` and fill in your MySQL password and a long random `SECRET_KEY`.
6. Start the server: `python app.py`
7. Open <http://localhost:5000>

## 4. Features
R1 register (+ "Email Already Exists", auto login) 
R2 login/logout with one generic error 
R3 private list, newest first  
R4 add 
R5 edit (save) title  
R6 mark done/not done 
R7 delete with confirmation 
R8 validation in browser (`static/app.js`) and server (`app.py`) with the exact messages 
R9 bcrypt hashes, only the given queries, always parameterized, `user_id` from the session 
R10 consistent responsive UI, empty state, error boxes, friendly error pages
Bonus: dark / light mode with a toggle button  · filters All / Open / Done · counter of open to-dos.

## 5. Screenshots
i put it in screenshot folder

## 6. Answers
(a) The to-do id comes from the browser, so anyone can send another user’s id. AND user_id = ? (taken from the session) makes the statement change zero rows if the to-do isn’t yours. Without it, any user could edit or delete other users’ to-dos.

(b) MySQL rejects the insert with error 1452, because todos.user_id must match an existing users.user_id. This is referential integrity, enforced by the foreign key constraint.

(c) If the database leaks, the real passwords must not be exposed. A bcrypt hash is one-way, salted and slow on purpose, so it is very hard to reverse. At login we only compare the typed password with the stored hash.

(d) NOT NULL only forbids NULL, and an empty text '' is a valid value. So only our own check (in the browser and on the server) can refuse an empty name.
