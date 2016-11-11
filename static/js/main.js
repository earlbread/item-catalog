/* main.js */

/* Add event listener for confirming when delete button is clicked */
(function() {
  var delete_buttons = document.querySelectorAll('.btn-delete');

  delete_buttons.forEach(function(element) {
    element.addEventListener('click', function(event) {
      if (!confirm('Are you sure?')) {
        event.preventDefault();
      }
    });
  });
})();

function imgError(image) {
      image.onerror = "";
      image.src = "/static/images/noimage.png";
      return true;
}
