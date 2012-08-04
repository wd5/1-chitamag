$(function() {
	$( "#filter_price_slider" ).slider({
		range: "min",
		value: 37,
		min: 800,
		max: 20000,
		slide: function( event, ui ) {
			$( ".filter_price_input input" ).val( ui.value );
		}
	});
	$( ".filter_price_input input" ).val( $( "#filter_price_slider" ).slider( "value" ) );
});