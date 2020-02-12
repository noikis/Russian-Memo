const wordEl = document.getElementById('word');
const wrongLettersEl = document.getElementById('wrong-letters');
const notification = document.querySelector('.notification');
const finalMessage = document.getElementById('final-message');
const playAgainBtn = document.getElementById('play-again');
const popup = document.querySelector('.popup-container');

const figureParts = document.querySelectorAll('.figure-part');

const correctLetters = [];
const wrongLetters = [];


const fetchCards = async () => {
    let response = await fetch("http://127.0.0.1:8000/api/cards");
    let data = await response.json();
    return data;
}

function displayWord(word) {
    wordEl.innerHTML = `
    ${word.split('').map(letter => `
        <span class="letter">
            ${correctLetters.includes(letter) ? letter : ''}
        </span>
    `).join('')}`;

    // replace new line by nothing globally 
    const innerWord = wordEl.innerText.replace(/\n/g, '');

    if (innerWord === word) {
        finalMessage.innerHTML = "Congratulation you won! &#128515;"
        popup.style.display = 'flex';

    }
}

function updateWrongLetters() {
    // Display Wrong Inputs
    wrongLettersEl.innerHTML = `
    ${wrongLetters.length > 0 ? "<p>Wrong</p>" : ""}
    ${wrongLetters.map(letter => `<span>${letter}</span>`)}
    `;

    // Display SVG Figures
    figureParts.forEach((part, index) => {
        const errors = wrongLetters.length;

        if (index < errors) {
            part.style.display = 'block';
        } else {
            part.style.display = 'none';
        }
    })

    // Lost
    if (wrongLetters.length === figureParts.length) {
        finalMessage.innerHTML = "Unfortunatly you lost &#128532; "
        popup.style.display = 'flex';
    }

}

function showNotification() {
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 2000);
}



fetchCards().then(cards => {
    let selectedWord = cards[Math.floor(Math.random() * cards.length)].fields.word;

    displayWord(selectedWord);

    window.addEventListener('keydown', (e) => {
        // if keyCode is a Letter ; otherKeys are keyCodes for "ё, б, ь, ю..."
        const otherKeys = [186, 188, 190, 219, 192, 222, 221];

        if ((e.keyCode >= 65 && e.keyCode <= 90) || otherKeys.includes(e.keyCode)) {
            const letter = e.key;

            // if input is correct
            if (selectedWord.includes(letter)) {

                if (!correctLetters.includes(letter)) {
                    correctLetters.push(letter);
                    displayWord(selectedWord)
                }
                // if input is wrong
            } else {
                if (!wrongLetters.includes(letter)) {
                    wrongLetters.push(letter);
                    updateWrongLetters();
                }
                else {
                    showNotification()
                }
            }
        }
    });
})
