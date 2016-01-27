$( document ).ready(function(){
	//Who won buttons/forms
	$(".who_won_form").hide();
	$(".who_won_but").click(function(){
		$(".who_won_form").hide();
		$(this).next().show()
	})
	$(".who_won_hide_but").click(function(){
		$(".who_won_form").hide();
	})
	
	//copy key to bottom of bracket
	key = $("#key").clone();
	$('#tourney').append(key);
	
	//*****SCROLLBARS*****//
	//since js is enabled, remove minwidth hack
	$('.minwidth').removeClass('minwidth')
	
	//make custom scrolls
	$(".bracket").mCustomScrollbar({
    	axis:"x", // horizontal scrollbar
		scrollButtons:{enable:true},
		advanced:{ 
			autoExpandHorizontalScroll: true 
		},
		mouseWheel:{ enable: false },
		theme: 'inset-3-dark',
	})
	//set scrollbar on top of div if needed
	if ($("#mCSB_1_scrollbar_horizontal").is(':visible')){
		$("#mCSB_1_scrollbar_horizontal").css('top', '0px');
		$("#mCSB_1_container").css('top', '20px');
	}
	if ($("#mCSB_2_scrollbar_horizontal").is(':visible')){
		$("#mCSB_2_scrollbar_horizontal").css('top', '0px');
		$("#mCSB_2_container").css('top', '20px');
	}
	//setup testing in case window size changes
	window.setInterval(function () {
        if ($("#mCSB_1_scrollbar_horizontal").is(':visible')){
			$("#mCSB_1_scrollbar_horizontal").css('top', '0px');
			$("#mCSB_1_container").css('top', '20px');
		}
		if ($("#mCSB_2_scrollbar_horizontal").is(':visible')){
			$("#mCSB_2_scrollbar_horizontal").css('top', '0px');
			$("#mCSB_2_container").css('top', '20px');
		}
		if ($("#mCSB_1_scrollbar_horizontal").is(':hidden')){
			$("#mCSB_1_container").css('top', '0px');
		}
		if ($("#mCSB_2_scrollbar_horizontal").is(':hidden')){
			$("#mCSB_2_container").css('top', '0px');
		}
    }, 300);
});