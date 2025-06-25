/*
    The following 4 functions make requests to app.py running on port 5000    

    fetchLetters()      ->      http://localhost:5000/api/game/today
    fetchFoundWords()   ->      http://localhost:5000/api/found_words?session_id=${sessionId}
    submitWord()        ->      http://localhost:5000/api/check_word
    restartGame()       ->      http://localhost:5000/api/restart

    to access these pages we will run a server via Python from the command line:
        C\:> python -m http.server 8000
        C\:> python ./app.py
    visiting http://localhost:8000 will start the game. as 127.0.0.1 is the default for Flask and we started the server on port 8000
*/

// save sessionId for tab persistence and to have unique individual tabs
const sessionId = sessionStorage.getItem('session_id') || crypto.randomUUID(); // if no sesh ID make up random one
sessionStorage.setItem('session_id', sessionId);

// global vars for letters used today, used by fetchLetters() and renderLetters()
let centerLetter = '';
let letters = [];

// An event listener that calls 4 functions when the DOM is ready, 2 automaticaly
document.addEventListener("DOMContentLoaded", function () {//waits until the DOM (Document Object Model) is fully loaded and parsed before running any code inside the function.
    fetchLetters();     // grab letters of the day
    fetchFoundWords();  // Load previously found words

    // handles pressing of submit and reset buttons
    document.getElementById("submitBtn").addEventListener("click", submitWord);   // if clicked calls submitWord()
    document.getElementById("restartBtn").addEventListener("click", restartGame); // if clicked calls restartGame()

    // submits letters typed into input element on the home page
    document.getElementById("wordInput").addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            submitWord();
        }
    });
});


// 1.
// GAME TODAY        'http://localhost:5000/api/game/today'

// retrieves data(letters) from the app.py server and updates the webpage based on the response
// uses responce from server to get todays letters and saves them to global variables then calls renderLetters()
function fetchLetters() {
    fetch('http://localhost:5000/api/game/today')
        .then(res => res.json())                            // grabs HTTPS responce in a json format
        .then(data => {                                     // then grabs the data
            centerLetter = data.center;                     // assign daily center letter to centerLetter
            letters = data.letters;                         // grabs letters to be printed to console for debug purposes
            console.log(letters);                           // debugging
            renderLetters();                                // callback, aka calls renderLetters() when done
        });
}


// used by fetchLetters()
// place letters on screen 
function renderLetters() {
    const letterDiv = document.getElementById("letters");                // grab container for letters to be displayed
    if (!letterDiv) return;                                              // if div id doesn't exist exit

    letterDiv.innerHTML = '';                                            // clear div's html

    // Reorder letters to put the center letter in the middle
    const orderedLetters = [...letters.filter(l => l !== centerLetter)]; // grab all letters except for center
    const midIndex = Math.floor(orderedLetters.length / 2);              // grab the middle of list without center letter
    //             splice(start, deleteCount, item1, ..., itemN)
    orderedLetters.splice(midIndex, 0, centerLetter);                    // Insert center letter in middle of that list

    // Render each letter
    orderedLetters.forEach(l => {
        const span = document.createElement("span");                // make span html elements for each letter
        span.className = "letter";                                  // add css class for style
        if (l === centerLetter) {
            span.classList.add("center");                           // add center css class for style
        }
        span.textContent = l.toUpperCase();
        span.addEventListener("click", () => handleLetterClick(l)); // handle if user clicks a letter ... adds it to wordInput css ID
        letterDiv.appendChild(span);                                // place all span elements into html page
    });
}
// function to display either clicked or typed letter into the display box
function handleLetterClick(letter) {
    const wordInput = document.getElementById("wordInput");         // grab element by ID
    wordInput.value += letter;                                      // add typed or clicked letter to display box
}


// 2.
// CHECK WORD       http://localhost:5000/api/check_word

// send possible word to server app.py
function submitWord() {
    const word = document.getElementById("wordInput").value.trim(); // remove any leading or trailing whitespace from the input
    if (!word) return;                                              // check for empty string ""

    // send info to app.py server using HTTPS POST
    fetch('http://localhost:5000/api/check_word', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },            // tells the server that the body of this request is in JSON format
        body: JSON.stringify({ word: word, session_id: sessionId }) // send word as word and sessionId as session_id to app.py
    })
        .then(res => res.json())                                    // the app.py server will respond with how to handle the users input
        .then(data => {
            const messageDiv = document.getElementById("message");  // grab element with id="message" to display message to user
            messageDiv.textContent = '';                            // clear it

            // give user appropriate response based on what they inputted
            if (data.result === "too short") {                                      // word < 4 letters long
                messageDiv.textContent = "Word too short!";
            } else if (data.result === "missing center") {                          // word does not contain center letter
                messageDiv.textContent = "Missing center letter!";
            } else if (data.result === "invalid") {                                 // word is NOT in the Data-Base
                messageDiv.textContent = "Invalid word!";
            } else if (data.result === "already found") {                           // word was alread used
                messageDiv.textContent = "Already found!";
            } else if (data.result === "ok") {                                      // word is VALID
                document.getElementById("score").textContent = data.total_points;
                document.getElementById("rank").textContent = data.rank;
                addWordToList(word);                                                // update found words
                if (data.pangram) {                                                 // handle Pangram
                    alert("Pangram!! Bonus Points!");
                    messageDiv.textContent = "Pangram!! Bonus Points!";
                }
            }

            document.getElementById("wordInput").value = '';                        // clear input for next word
        });
}


// 3.
// FOUND WORDS ? SESSONID      http://localhost:5000/api/found_words?session_id=${sessionId}

// retrieves data(words already found per session) from the app.py server and updates the webpage based on the response
function fetchFoundWords() {
    // ? is a query param and & is for key value pairs example: https://example.com/search?query=books&sort=asc
    fetch(`http://localhost:5000/api/found_words?session_id=${sessionId}`) 
        .then(res => res.json())
        .then(data => {
            data.found_words.forEach(word => addWordToList(word));              // call addWordToList() to make list of already found words
            document.getElementById("score").textContent = data.total_points;   // display users existing score
            document.getElementById("rank").textContent = data.rank;            // display users existing rank
        });
}

// creates a list of found words for user to see on screen
function addWordToList(word) {
    const list = document.getElementById("foundWords");
    const item = document.createElement("li");
    item.textContent = word.toUpperCase();
    list.appendChild(item);
}


// 4.
// RESTART       http://localhost:5000/api/restart

// handle restarting of game via restard button
function restartGame() { 
    fetch('http://localhost:5000/api/restart', {            // send restart message to app.py server
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },    // tells the server that the body of this request is in JSON format

        body: JSON.stringify({ session_id: sessionId })     // tell it which session aka tab to restart, leaves other tabs alone
    })
        .then(res => res.json())
        .then(data => {
            if (data.result === "restarted") {              // reset display for user
                document.getElementById("foundWords").innerHTML = '';
                document.getElementById("score").textContent = 0;
                document.getElementById("rank").textContent = "Beginner";
            }
        });
}
