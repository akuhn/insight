	$('#navbar').affix()
	function initialize() {
			
		var mapOptions = {
			mapTypeId: google.maps.MapTypeId.ROADMAP,
			center: new google.maps.LatLng(49.285, -123.13),
			zoom: 13,
			disableDefaultUI: true,
			zoomControl: true,
			panControl: true
		};
		var map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

		jQuery.fn.flash = function( )
		{
		    var current = this.css( 'color' );
		    this.animate( { 'background-color': 'rgb(255,255,127)' }, 500 );
		    this.animate( { 'background-color': 'white' }, 500 );
		}


		path.forEach(function(each) {
			var loc = new google.maps.LatLng(each[0],each[1])
    var marker = new google.maps.Marker({
        position: loc,
        map: map,
					icon: {
						  url: each[3],
					},
					shadow: {
						  url: 'http://maps.google.com/mapfiles/shadow50.png',
							anchor: new google.maps.Point(9, 35),
					}
    })
			$('#'+each[2]).data('marker',marker)
	    google.maps.event.addListener(marker, 'click', function(){
				var offset = $('#'+each[2]).offset();
				$('html, body').animate({
				    scrollTop: offset.top - 200,
				    scrollLeft: offset.left
				});
				$('#'+each[2]).flash();
			});
		})
		
			
	}

