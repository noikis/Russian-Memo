// // Custom Elements
// class Toast extends HTMLElement {
//     constructor() {
//         super();
//         this.message = this.getAttribute('message');
//         this.color = this.getAttribute('color');
//         this.init = M.toast({
//             html: this.message,
//             classes: `rounded ${this.color}`
//         });
//     }
// }
// customElements.define('material-toast', Toast);


// // SideNav init 
// const sideNav = document.querySelector(".sidenav");
// M.Sidenav.init(sideNav, {
//     menuWidth: 100
// });




// // Get ride of helper text in forms
// const helpers = document.querySelectorAll('.helptext');
// for (const helper of helpers) {
//     helper.style.display = "none";
// }

// // get current year in footer
// const year = new Date();
// document.querySelector("#copyright-year").textContent = year.getFullYear()


// Fixed Buttons
const fixedBtns = document.querySelectorAll('.fixed-action-btn')
M.FloatingActionButton.init(fixedBtns);


// Dropdown Button
document.addEventListener('DOMContentLoaded', function () {
    // const dropDown = document.querySelectorAll('.dropdown-trigger');
    // M.Dropdown.init(dropDown);

    const selects = document.querySelectorAll('select');

    for (let select of selects) {
        select.classList.add('browser-default');
    }
});

