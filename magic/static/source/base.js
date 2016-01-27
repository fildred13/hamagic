$(document).ready(function() { 
        $(".sorted_table").tablesorter(); 
		
		//prevent double clicking of links so program doesnt break
		$(".tourney_link").one('click',function(e){
    		$(this).on('click',function(ev){
      			ev.preventDefault();
    		});  
		});
}); 