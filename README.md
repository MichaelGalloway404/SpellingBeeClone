# Spelling Bee Clone Senior Capstone Project
  
For My Senior Project at Eastern Oregon University, we were tasked with creating a Clone of the New York Times Spelling Bee app.  
Our requirements were:  
>>Front end using JavaScript, HTML, and CSS. 
>>REST API using Pythons Flask library
>>And MySQL for the database containing 80k words provided by the professor via a word.txt file  
  
To run locally on WINDOWS:  
Step 1:  
>>Download MySQL installer from https://dev.mysql.com/downloads/installer/  
>>Go through installation steps and write down your user name and password  
      For this project I just used username = root and password = root  
Step 2:  
  
>>If added to your environment variables  
>>From command line run the this command:  
>>>>.\mysql.exe -u root -p  
>>Else cd to C:\Program Files\MySQL\MySQL Server 8.0\bin
>>then run .\mysql.exe -u root -p  
  
>>That command should open an SQL command line in the same window  
>>Then from the SQL command line run the this command:  
      
            -- Create database (if you haven't yet)  
            CREATE DATABASE IF NOT EXISTS spellingbee;  
            USE spellingbee;  
            -- Table for valid dictionary words  
            CREATE TABLE valid_words (  
                id INT AUTO_INCREMENT PRIMARY KEY,  
                word VARCHAR(100) UNIQUE NOT NULL  
            );  
  
            -- Table for user sessions and found words  
            CREATE TABLE user_stats (  
                id INT AUTO_INCREMENT PRIMARY KEY,  
                session_id VARCHAR(255) NOT NULL,  
                found_words TEXT, -- will store JSON list of words  
                date_played DATE,  
                UNIQUE (session_id, date_played)  
            );  
      -- are comments and this will create our Data Bases with needed tables  
>>Or you can use the setup.sql that contains these same lines of code.  
>>The file sqlCREATE_TABLES.txt contains these lines of code as well.  
  
Step 3:  
>>Make sure you have word.txt in the same folder as loadTablesSQL.py  
>>Make sure in loadTablesSQL.py you change the username and password to what you set it in your MySQL install  
>>Run loadTablesSQL.py
>>From command line:
>>>> python ./loadTablesSQL.py
   
>>This will fill you DataBase with the 80K+ words from words.txt  
  
Step 4:  
>>Great now make sure app.py also has the correct username and password to what you set it in your MySQL install  
  
Step 5:  
>>Now we are ready to run, you will need two command prompts  
>>In the 1st cmd type:  
>>>>python -m http.server 8000
  
>>This will start our server so make sure "python -m http.server 8000" is ran 1st  
>>In the 2nd cmd type:  
>>>>python app.py
  
>>now our app is up and running on http://localhost:8000/  
      
Final step:  
>>Open a Browder and visit the URL http://localhost:8000/  
>>Enjoy the Game!  
