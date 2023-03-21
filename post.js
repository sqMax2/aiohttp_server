$(function(){
  let text = $("#news_text");
  text.width(400);
  text.height(400);
  text.attr('placeholder', 'news text');
  let response = $("#response");

  function send(msg){
    console.log('sending: ' + msg)
    fetch('/news', {
      method: 'POST',
      headers: {
        "Content-Type": "application/json;odata=verbose",
      },
      body: JSON.stringify({
        "__metadata": { "data": msg },
      })
    })
        .then(result => result.json())
        .then(data => response.html(JSON.stringify(data)));
  }

  $('#submit').click(function() {
    send(text.val());
    text.val('').focus();
    return false;
  });

});


