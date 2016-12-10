/* main.js */

function imgError(image) {
      image.onerror = "";
      image.src = "/static/images/noimage.png";
      return true;
}

function sendTokenToServer(url, data) {
  var csrf_token = $('meta[name=csrf-token]').attr('content');

  $.ajax({
    type: 'POST',
    url: url + '?_csrf_token=' + csrf_token,
    processData: false,
    data: data,
    contentType: 'application/octet-stream; charset=utf-8',
  }).done( function(result) {
    // Handle or verify the server response if necessary.
    if (result) {
      console.log('Successfully logged in');
      window.location.href = "/category/all";
    } else if (authResult['error']) {
      console.log('There was an error: ' + authResult['error']);
    } else {
      console.log('Failed to make a server-side call. Check your configuration and console.');
    }
  }).fail( function(jqXHR, textStatus) {
    console.log( "Request failed: " + textStatus );
    window.location.href = "/login";
  });
}

function googleSignIn(authResult) {
  if (authResult['code']) {
    url = '/gconnect';
    data = authResult['code'];

    sendTokenToServer(url, data);
  }
}

function googleSignInFailure() {
  console.log('Google Sign in is failed.');
}

/* Facebook SDK for JavaScript */
window.fbAsyncInit = function() {
  FB.init({
    appId      : '154713091667161',
    xfbml      : true,
    version    : 'v2.6'
  });
};

// Load the SDK asynchronously
(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function facebookSignIn() {
  var access_token = FB.getAuthResponse()['accessToken'];
  FB.api('/me', function(response) {
    url = '/fbconnect';
    data = access_token;
    sendTokenToServer(url, data);
  });
}
