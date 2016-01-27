$(document).ready(function(){
  var container = $('#cardImageHolder');
  
  //preload all the images for the deck, then change the mouseenter function to just grab this instead of ajaxing again. OR load cards as needed, but save loaded images to hidden container, then load that if it's there next time.
  
  $('.card_link').click(function(e){
	e.preventDefault();
	var target = $(this).data('gatherer');
	window.open(target);
  	});
});