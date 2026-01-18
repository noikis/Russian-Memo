// TODO: Change host before deployment
const host = "https://kameron-benefic-madelaine.ngrok-free.dev/"
const tg = window.Telegram?.WebApp;
username = tg?.initDataUnsafe?.username || "noikis";


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
    let response = await fetch(`${host}/api/users/${username}/cards`);
    let data = await response.json();
    return data;
}

function displayWord(word) {
    const letters = word.split('');
    const letterCount = letters.filter(letter => letter !== ' ').length;
    wordEl.classList.toggle('long-word', letterCount > 12);
    wordEl.classList.toggle('very-long-word', letterCount > 18);

    wordEl.innerHTML = `
    ${letters.map(letter => {
        const isSpace = letter === ' ';
        return `
        <span class="letter${isSpace ? ' space' : ''}">
            ${isSpace ? '&nbsp;' : (correctLetters.includes(letter) ? letter : '')}
        </span>
        `;
    }).join('')}`;

    const solvedWord = letters.map(letter => {
        if (letter === ' ') {
            return ' ';
        }
        return correctLetters.includes(letter) ? letter : '';
    }).join('');

    if (solvedWord === word) {
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
