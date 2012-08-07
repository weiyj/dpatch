
(function( $, undefined ) {

$.widget( "ui.navigator", {

	options: {
		selected: null,
	},

	_create: function() {
		this._navigator();
	},

	_navigator: function() {
		var self = this,
			 o = this.options;

		this.list = this.element.find( "ol,ul" ).eq( 0 );
		this.lis = $( " > li:has(a[href])", this.list );
		this.anchors = this.lis.map(function() {
			return $( "a", this )[ 0 ];
		});

		this.element.addClass("ui-nav");
		this.lis.addClass("ui-nav-menu");
		this.anchors.addClass("ui-nav-link");

		if (o.selected != null && o.selected >= 0 && this.anchors.length ) {
			this.lis.eq( o.selected ).addClass( "ui-nav-selected" );
			this.anchors.eq(o.selected).bind('click', function () {
					return false;
			});
		}

		this.lis.bind('mouseover', function(e) {
			$(this).addClass('hover').find('a:eq(0)').addClass('hover');
		})
		.bind('mouseout', function(e) {										
			$(this).removeClass('hover').find('a:eq(0)').removeClass('hover');
		});
	},
});

})( jQuery );