(function( $, undefined ) {

$.widget( "ui.lists", {

	options: {
		selected: null,
		removeHeight: 0,
		navWidth: 280,
		ajaxOptions: null,
	},

	_create: function() {
		this._listify();
	},

	_listify: function() {
		var self = this;
		var elem = this.element;
		var o = this.options;

		this.list = this.element.find( "ol,ul" ).eq( 0 );
		this.title = $( " > li:not(:has(a[href]))", this.list ).eq( 0 );
		this.lis = $( " > li:has(a[href])", this.list );
		this.anchors = this.lis.map(function() {
			return $( "a", this )[ 0 ];
		});
		this.panel = this.element.find(".ui-list-panel").eq(0);

		if (this.panel.length == 0) {
			this.panel = $('<div></div>').addClass("ui-list-panel")
												  .appendTo(this.element);
		}

		this.nav = $('<div></div>').addClass('ui-list-nav')
		this.list.wrap(this.nav);

		this.btnclose = $("<span></span>").addClass("ui-list-title-close");
		this.title.addClass("ui-list-title").prepend(this.btnclose);
		this.element.addClass("ui-lists");

		elem.height($(window).height() - o.removeHeight);
		elem.find(".ui-list-nav").width(o.navWidth)
		elem.find(".ui-list-panel").width($(window).width() - o.navWidth - 20);

		if ( o.selected === null || o.selected >= this.lis.length)
			o.selected = this.lis.length ? 0 : -1;

		this.lis.each(function( i, li ) {
			$(li).prepend($("<span></span>").addClass("ui-list-nav-arrow"));
			$(li).attr('id', i);
		});

		if ( o.selected >= 0 && this.lis.length ) {
			this.lis.eq( o.selected ).addClass( "ui-list-nav-selected" );
			this.load( o.selected );
		}

		this.lis.bind('mouseover', function(e) {
			$(this).addClass('hover');
		})
		.bind('mouseout', function(e) {										
			$(this).removeClass('hover');
		})
		.bind('click', function(e) {
			o.selected = $(this).attr('id');
			self.lis.removeClass('ui-list-nav-selected');
			$(this).addClass('ui-list-nav-selected');
			self.load( o.selected );
			return false;
		});

		this.btnclose.bind('mouseover', function(e) {
			$(this).addClass('hover');
		})
		.bind('mouseout', function(e) {										
			$(this).removeClass('hover');
		})
		.bind('click', function(e) {
			return false;
		});

		this.anchors.bind('click', function () {
			return true;
		});

		this.btnclose.bind('click', function () {
			//elem.find(".ui-list-nav").width(10)
			//elem.find(".ui-list-panel").width($(window).width() - 30);
		});

      // resize  event handlers;
		$(window).resize(function() {
			elem.height($(window).height() - o.removeHeight);
			elem.find(".ui-list-panel").width($(window).width() - o.navWidth - 20);
		});
	},

	load: function( index ) {
		var self = this,
			o = this.options,
			url = this.anchors[index].href;

		this.abort();

		this.xhr = $.ajax( $.extend( {}, o.ajaxOptions, {
			url: url,
			success: function( r, s ) {
				self.panel.html( r );
				try {
					o.ajaxOptions.success( r, s );
				}
				catch ( e ) {}
			},
			error: function( xhr, s, e ) {
				self.panel.html("Load " + url + " Error!" + e);
				try {
					o.ajaxOptions.error( xhr, s, index, a );
				}
				catch ( e ) {}
			}
		} ) );

		return this;
	},

	abort: function() {
		// terminate pending requests from other lists
		if ( this.xhr ) {
			this.xhr.abort();
			delete this.xhr;
		}
		return this;
	},

});

})( jQuery );