(function () {
  var knoppen = document.querySelectorAll('.so-filter button');
  var kaarten = document.querySelectorAll('.so-card');
  var groepen = document.querySelectorAll('.so-grid');
  knoppen.forEach(function (k) {
    k.addEventListener('click', function () {
      var f = k.dataset.filter;
      knoppen.forEach(function (b) { b.setAttribute('aria-pressed', b === k ? 'true' : 'false'); });
      kaarten.forEach(function (c) { c.hidden = f !== 'alle' && c.dataset[f] !== 'ja'; });
      groepen.forEach(function (g) {
        var zichtbaar = g.querySelectorAll('.so-card:not([hidden])').length > 0;
        g.hidden = !zichtbaar;
        g.previousElementSibling.hidden = !zichtbaar;
      });
    });
  });
})();
