recipe_names = document.getElementsByClassName("recipe_name");
favorites_input = document.getElementById("favorites_search");
if (favorites_input) {
  favorites_input.addEventListener("input", function (event) {
    text_input = event.target.value.toLowerCase();
    for (let i = 0; i < recipe_names.length; i++) {
      if (!recipe_names[i].textContent.toLowerCase().match(text_input)) {
        recipe_names[i].parentElement.classList.add("hidden");
      } else {
        recipe_names[i].parentElement.classList.remove("hidden");
      }
    }
  });
}
