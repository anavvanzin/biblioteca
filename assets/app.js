(function () {
  var grid = document.getElementById("grid");
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
  var searchInput = document.getElementById("search");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var countEl = document.getElementById("result-count");
  var emptyEl = document.getElementById("empty-state");

  var active = { tema: new Set(), lang: new Set(), status: new Set() };

  function normalize(s) {
    return (s || "").toString().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function applyFilters() {
    var q = normalize(searchInput ? searchInput.value : "");
    var visible = 0;
    cards.forEach(function (card) {
      var tema = card.getAttribute("data-tema");
      var lang = card.getAttribute("data-lang");
      var status = card.getAttribute("data-status");
      var haystack = normalize(card.getAttribute("data-search"));

      var okTema = active.tema.size === 0 || active.tema.has(tema);
      var okLang = active.lang.size === 0 || active.lang.has(lang);
      var okStatus = active.status.size === 0 || active.status.has(status);
      var okSearch = q === "" || haystack.indexOf(q) !== -1;

      var show = okTema && okLang && okStatus && okSearch;
      card.style.display = show ? "" : "none";
      if (show) visible++;
    });
    if (countEl) {
      countEl.textContent = visible === 1 ? "1 texto encontrado" : visible + " textos encontrados";
    }
    if (emptyEl) {
      emptyEl.classList.toggle("visible", visible === 0);
    }
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var group = chip.getAttribute("data-group");
      var value = chip.getAttribute("data-value");
      var pressed = chip.getAttribute("aria-pressed") === "true";
      chip.setAttribute("aria-pressed", pressed ? "false" : "true");
      if (pressed) {
        active[group].delete(value);
      } else {
        active[group].add(value);
      }
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  applyFilters();
})();
