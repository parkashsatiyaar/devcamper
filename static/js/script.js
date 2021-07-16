const form = document.querySelector("form");
form.addEventListener("submit", processing);
function loading() {
  document.getElementById("loading").style.display = "none";
}
function processing() {
  document.getElementById("loading").style.display = "block";
}

function mySubmit(id) {
  document.getElementById(id).submit();
}
