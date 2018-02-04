var comments = (function() {
  "use strict";

  var formSubmit = function(event) {
    event.preventDefault();

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'https://o6z21z4pxj.execute-api.eu-west-1.amazonaws.com/dev');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status === 200) {
          form.insertAdjacentHTML('afterend', '<p class="f4 tc">Your comment is processing and will show shortly.</p>')
          form.parentNode.removeChild(form);
        } else if (xhr.status !== 200) {
            alert('Could not post comment');
        }
    };

    var el;
    var data = [];

    var inputs = form.querySelectorAll('input:not([type=submit]), textarea');
    for (var i = 0; i < inputs.length; i++) {
      el = inputs[i];
      data.push((el.name || el.id) + '=' + el.value)
    }

    xhr.send(encodeURI(data.join('&')));
    return false
  }

  var slug = document.currentScript.dataset.slug;
  var inputSelector = document.currentScript.dataset.inputSelector;
  var outputSelector = document.currentScript.dataset.outputSelector;
  var outputNode = document.querySelector(outputSelector);

  var form = document.querySelector(inputSelector);
  form.addEventListener('submit', formSubmit, true);


  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'https://s3-eu-west-1.amazonaws.com/zappa-comments-input/indexes/' + slug + '.json')
  xhr.onload = function() {
    if (xhr.status !== 200) {
      console.warn('Unable to fetch comments')
    }

    var resp = JSON.parse(xhr.response);
    var comment;
    var html;
    for (var i = 0; i < resp.comments.length; i++) {
      comment = resp.comments[i];

      var date = new Date(comment.created_at);
      var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'][date.getMonth()];
      comment.created_at_string = date.getDate() + ' ' + month + ' ' + date.getFullYear();

      var template = document.querySelector('.comment-template');
      Mustache.parse(template.innerText);
      html = Mustache.render(template.innerText, {comment: comment});
      outputNode.insertAdjacentHTML('beforeend', html)
    }
    window.comments = resp.comments;
  }
  xhr.send();
  return {}

})();
