(function () {
  var form = document.getElementById("filters");
  var table = document.getElementById("buyers");
  if (!form || !table) return;

  var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr[data-naam]"));
  var groups = Array.prototype.slice.call(table.querySelectorAll("tbody tr.group-row"));
  var count = document.getElementById("count");
  var empty = document.getElementById("empty");
  var reset = document.getElementById("reset");

  function apply() {
    var wantGeld = form.elements.geld.checked;
    var wantRetour = form.elements.retour.checked;
    var wantKapot = form.elements.kapot.checked;
    var shown = 0;

    rows.forEach(function (row) {
      var ok =
        (!wantGeld || row.dataset.geld === "true") &&
        (!wantRetour || row.dataset.retour === "ja") &&
        (!wantKapot || row.dataset.kapot === "ja");
      row.hidden = !ok;
      if (ok) shown++;
    });

    groups.forEach(function (g) {
      var any = rows.some(function (r) {
        return r.dataset.group === g.dataset.group && !r.hidden;
      });
      g.hidden = !any;
    });

    count.textContent = shown === 1 ? "1 inkoper" : shown + " inkopers";
    empty.hidden = shown !== 0;
    table.hidden = shown === 0;
  }

  form.addEventListener("change", apply);
  reset.addEventListener("click", function () {
    form.reset();
    apply();
  });
  apply();
})();
