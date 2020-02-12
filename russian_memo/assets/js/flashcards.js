const flipBtn = document.getElementById("flip-btn");
const flashcard = document.getElementById('flashcard');
const evaluation = document.getElementById('evaluation');
const selects = document.querySelectorAll("select");
const hideEls = document.querySelectorAll('.hide');

for (let select of selects) {
    select.classList.add('browser-default');
}


flipBtn.addEventListener('click', () => {
    flashcard.style.transform = "rotateY(180deg)";
    flipBtn.style.display = "none";

    for (const hide of hideEls) {
        hide.classList.remove('hide');

    }
})

