function ajaxShowDialog(dlg, type, url, args) {
	$.ajax({
		type: type,
		url: url,
		data: args,
		success: function(data){
			$(dlg).html(data).dialog('open'); 
		},
		error: function(xhr, status, throwerr){
			alert(xhr);
		}
	});	
}

function showModelDialog(url, args, type, grid) {
	$.blockUI(); 
	$.ajax({
		type: type,
		url: url,
		data: args,
		success: function(data){
			$.blockUI({ message: "<h1>" + data + "</h1>" });
			setTimeout($.unblockUI, 1000);
			if (grid && grid.length != 0)
				$(grid).flexReload();
		},
		error: function(xhr, status, throwerr){
			$.blockUI({ message: "<h1>ERROR: " + url + "</h1>" });
			setTimeout($.unblockUI, 1000);
		}
	});
}

function alertBox(msg) {
	$.blockUI({ message: "<h1>" + msg + "</h1>" });
	setTimeout($.unblockUI, 1000);			
}
