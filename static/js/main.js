/* main.js */

function imgError(image) {
      image.onerror = "";
      image.src = "/static/images/noimage.png";
      return true;
}

function logout() {
  var auth2 = gapi.auth2.getAuthInstance();
  auth2.signOut().then(function () {
    window.location.href = "/logout";
  });
}

function googleSignIn(authResult) {
  var csrf_token = $('meta[name=csrf-token]').attr('content');

  if (authResult['code']) {
    $.ajax({
      type: 'POST',
      url: '/gconnect?_csrf_token=' + csrf_token,
      processData: false,
      data: authResult['code'],
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {
        // Handle or verify the server response if necessary.
        if (result) {
          console.log('Successfully logged in');
          window.location.href = "/category/all";
        } else if (authResult['error']) {
          console.log('There was an error: ' + authResult['error']);
        } else {
          console.log('Failed to make a server-side call. Check your configuration and console.');
        }
      }
    });
  }
}

function googleSignInFailure() {
  console.log('Google Sign in is failed.');
}
