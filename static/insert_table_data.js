let currentNextGuessBox = 1;
let guessable_conflicts_list = [];
let lost = false;

document.querySelectorAll('.conflict-option').forEach(el => {
  el.addEventListener('click', () => submitGuess(el.dataset.name));
});

/* When the user clicks on the search bar,
toggle between hiding and showing the dropdown content */
document.addEventListener("click", function(event){
  isVisible = document.getElementById("myDropdown").checkVisibility()
  if (event.target.closest("#myInput")){
    if (isVisible){
      return
    }

    else{
      document.getElementById("myDropdown").classList.toggle("show");
    }
  }

  else if (isVisible){
    document.getElementById("myDropdown").classList.toggle("show");
  }
})

function filterFunction() {
  const input = document.getElementById("myInput");
  const filter = input.value.toUpperCase();
  const div = document.getElementById("myDropdown");
  const a = div.getElementsByTagName("a");
  for (i = 0; i < a.length; i++) {
    const txtValue = a[i].textContent || a[i].innerText;
    guessable_conflicts_list[i] = txtValue;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } 
    
    else {
      a[i].style.display = "none";
    }
  }
}

function ShowNotification(notificationText){
  let notificationBox = document.getElementById("bottomNotification");
  notificationBox.classList.remove("fade-in-fade-out");
  void notificationBox.offsetWidth; // forces reflow so re-adding the class replays the animation
  notificationBox.classList.add("fade-in-fade-out");
  notificationBox.textContent = notificationText;
}

function RemovePlayerGuessing(){
  document.getElementById("myInput").remove();
  document.getElementById("myDropdown").remove();
}

function ShowInfo(result){
  const info_to_id_dict = {
    "start": "startBox",
    "end": "endBox",
    "victors": "victorsBox",
    "defeated": "defeatedBox",
    "name": "conflictNameLine",
    "none" : "none"
  }
  console.log(result.new_info_type)
  for (i = 0; i < result.new_info_type.length; i++){
    const new_info_type = result.new_info_type[i];
    const new_info = result.new_info[i];
    const item_id = info_to_id_dict[new_info_type];
    console.log(new_info)
    if (item_id == "none"){
      continue
    }
    document.getElementById(item_id).innerHTML = document.getElementById(item_id).innerHTML.replace('???', new_info);
  }
}

async function submitGuess(playerGuessText) {
  let previousGuesses = [];
  const guessBoxes = document.getElementsByClassName("guessBox");
  for (i = 0; i < guessBoxes.length; i++){
    const prevGuessText = guessBoxes[i].textContent;
    previousGuesses[i] = prevGuessText;
  }

  if (!previousGuesses.includes(playerGuessText)){
    document.getElementById("guessBox"+currentNextGuessBox).textContent = playerGuessText;
    currentNextGuessBox++;

    const remainingAttempts = currentNextGuessBox - 2;
    const response = await fetch('/guess', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: playerGuessText, num_attempts: remainingAttempts})
    });

    const result = await response.json();
    ShowInfo(result);
    if (result.correct){
      RemovePlayerGuessing();
      ShowNotification("Correct! You WON!!!");
    }

    else{
      if (currentNextGuessBox > 5){
        lost = true;
      }

      if (lost){
        RemovePlayerGuessing();
        ShowNotification("You lost :(");
      }

      else{
        ShowNotification("Incorrect");
      }
    }
  }

  else{
    ShowNotification("Already guessed!");
  }
}

