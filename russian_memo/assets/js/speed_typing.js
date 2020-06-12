window.addEventListener('load', init);

// DOM Elements
const wordInput = document.querySelector('#word-input');
const currentWord = document.querySelector('#current-word');
const timeDisplay = document.querySelector('#time');
const message = document.querySelector('#message');
const seconds = document.querySelector('#seconds');
const speakerBtn = document.querySelector('#speaker');
const scoreDisplay = document.querySelector('#score');
const popup = document.querySelector('.popup-container');

/**
 * different Levels of the game
 * @type {object}
 * @property {number} easy - Easy difficulty
 * @property {number} medium - Midium difficulty
 * @property {string} hard - Maximum difficulty
 */
const levels = {
  easy: 10,
  medium: 5,
  hard: 3,
};

/**
 * Current Level
 * @default easy
 */
const currentLevel = levels.easy;

// Speech Synthesis API
const synth = window.speechSynthesis;

// Variables
let time = currentLevel;
let score = 0;
let gameOver;
let randIndex = 0;
let voices = [];
let inputFocus = false;

/**
 * Click on the speak icon
 * @event speak
 */
speakerBtn.addEventListener('click', speak);

// Functions
function init() {
  /**
   * Fetch cards from the API
   * @param none
   * @returns {Array}
   */

  const fetchCards = async () => {
    let response = await fetch('http://127.0.0.1:8000/api/cards');
    let data = await response.json();
    console.log(data);
    return data;
  };

  seconds.innerHTML = currentLevel;
  // Load word from array
  fetchCards().then((words) => {
    showWord(words);

    // Start matching on word input
    wordInput.addEventListener('input', () => {
      inputFocus = true;

      if (matchWords(words)) {
        gameOver = false;
        time = currentLevel + 1;
        showWord(words);
        wordInput.value = '';
        score++;
        scoreDisplay.textContent = score;
      }
    });
    // Call countdown every second
    setInterval(countdown, 1000);
  });
}

// Match currentWord to wordInput
function matchWords(words) {
  if (words[randIndex].fields.translation === wordInput.value) {
    message.innerHTML = 'Correct!!!';
    return true;
  } else {
    message.innerHTML = '';
    return false;
  }
}

// Pick & show random word
function showWord(words) {
  // Generate random array index
  randIndex = Math.floor(Math.random() * words.length);
  // Output random word
  currentWord.innerHTML = words[randIndex].fields.word;
}

// Countdown timer
function countdown() {
  if (time > 0 && inputFocus) {
    time--;
  } else if (time === 0) {
    gameOver = true;
    popup.style.display = 'flex';
    wordInput.disabled = true;
  }
  // Show time
  timeDisplay.innerHTML = time;
}

getVoices = () => {
  voices = synth.getVoices();
};

// Fill the voice array
getVoices();
if (synth.onvoiceschanged !== undefined) {
  synth.onvoiceschanged = getVoices;
}

function speak() {
  // Check if Already speaking
  if (synth.speaking) {
    console.error('Already speaking...');
    return;
  }

  // Sending a Speech Request to the API
  const speakRequest = new SpeechSynthesisUtterance(currentWord.innerHTML);

  // Run when the speacking will be done:
  speakRequest.onend = (e) => {};

  // Error
  speakRequest.onerror = (e) => {
    console.log('Speacking Error!');
  };

  // Choose the Accent
  speakRequest.voice = voices[0];

  speakRequest.rate = 1;
  speakRequest.pitch = 1.5;

  // Speak
  synth.speak(speakRequest);
}
