$(document).ready(function(){
  var container = $('#cardImageHolder');
  
  //preload all the images for the deck, then change the mouseenter function to just grab this instead of ajaxing again. OR load cards as needed, but save loaded images to hidden container, then load that if it's there next time.
  
  $('.bumpin a').mouseenter(function(){
    doAjax($(this).attr('href'));
    return false;
  });
  
  function doAjax(url){
    // if it is an external URI
    if(url.match('^http')){
      // call YQL
      $.getJSON("http://query.yahooapis.com/v1/public/yql?"+
                "q=select%20*%20from%20html%20where%20url%3D%22"+
                encodeURIComponent(url)+
                "%22&format=xml'&callback=?",
        // this function gets the data from the successful 
        // JSON-P call
        function(data){
          // if there is data, filter it and render it out
          if(data.results[0]){
            var data = filterData(data.results[0]);
			var src = $(data).find('.leftCol img').first().attr('src');
			var fixedImageSrc = src.replace("../../", "http://gatherer.wizards.com/");
			var image = $(data).find('.leftCol img').first().attr('src', fixedImageSrc);
            container.html(image);
          // otherwise tell the world that something went wrong
          } else {
            var errormsg = "<p>Error: can't load the page.</p>";
            container.html(errormsg);
          }
        }
      );
    // if it is not an external URI, use Ajax load()
    } else {
      $('#target').load(url);
    }
  }
  // filter out some nasties
  function filterData(data){
    data = data.replace(/<?\/body[^>]*>/g,'');
    data = data.replace(/[\r|\n]+/g,'');
    data = data.replace(/<--[\S\s]*?-->/g,'');
    data = data.replace(/<noscript[^>]*>[\S\s]*?<\/noscript>/g,'');
    data = data.replace(/<script[^>]*>[\S\s]*?<\/script>/g,'');
    data = data.replace(/<script.*\/>/,'');
    return data;
  }
});