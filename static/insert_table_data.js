currentNextGuessBox = 1;
const guessable_conflicts_list = [];

/* When the user clicks on the search bar,
toggle between hiding and showing the dropdown content */
function toggleDropdownVisibility() {
  document.getElementById("myDropdown").classList.toggle("show");
}

function filterFunction() {
  var input, filter, ul, li, a, i;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  div = document.getElementById("myDropdown");
  a = div.getElementsByTagName("a");
  for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    guessable_conflicts_list[i] = txtValue;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } else {
      a[i].style.display = "none";
    }
  }
}

function ShowNotification(notificationText){
  notificationBox = document.getElementById("bottomNotification");
  notificationBox.classList.remove("fade-in-fade-out");
  void notificationBox.offsetWidth; // forces reflow so re-adding the class replays the animation
  notificationBox.classList.add("fade-in-fade-out");
  notificationBox.textContent = notificationText;
}

function selectConflict(nameOfGuess){
  const previousGuesses = [];
  guessBoxes = document.getElementsByClassName("guessBox");
  for (i = 0; i < guessBoxes.length; i++){
    guessText = guessBoxes[i].textContent;
    previousGuesses[i] = guessText;
  }

  if (!previousGuesses.includes(nameOfGuess)){
    document.getElementById("guessBox"+currentNextGuessBox).textContent = nameOfGuess;
    currentNextGuessBox++;
  }

  else{
    ShowNotification("Already guessed!")
  }
}
