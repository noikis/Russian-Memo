const date = new Date();
document.querySelector(".year").innerHTML = date.getFullYear();

//  fade out effect on error messages using jquery
setTimeout(() => {
  $("#message").fadeOut("slow");
}, 1000);
