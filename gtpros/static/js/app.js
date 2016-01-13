(function($) {

	"use strict";

	$('.btn-group button[data-calendar-nav]').each(function() {
		var $this = $(this);
		$this.click(function() {
			calendar.navigate($this.data('calendar-nav'));
		});
	});

	$('.btn-group button[data-calendar-view]').each(function() {
		var $this = $(this);
		$this.click(function() {
			calendar.view($this.data('calendar-view'));
		});
	});

}(jQuery));

function get_events(actividades, hitos) {
	
	
	var jsonEventos = [];
	
	if(actividades !== null && actividades.length > 0) {
		var jsonActividades = JSON.parse(actividades);
		
		$.each(jsonActividades, function(index, actividad) {
			var item = {};
			item["id"] = actividad.id;
			item["title"] = actividad.nombre;
			item["url"] = "/event_detail?id=".concat(actividad.id);
			item["class"] = "event-warning";
			var iniDate = new Date(actividad.fecha_inicio);
			item["start"] = "".concat(iniDate.getTime());
			var endDate = new Date(actividad.fecha_fin);
			item["end"] = "".concat(endDate.getTime());
			
			jsonEventos.push(item);
		});
	}
	
	if(hitos !== null && hitos.length > 0) {
		var jsonHitos = JSON.parse(hitos);
		$.each(jsonHitos, function(index, hito) {
			var item = {};
			item["id"] = hito.id;
			item["title"] = hito.nombre;
			item["url"] = "/event_detail?id=".concat(hito.id);
			item["class"] = "event-info";
			var date = new Date(hito.fecha);
			item["start"] = "".concat(date.getTime());
			item["end"] = "".concat(date.getTime());
			
			jsonEventos.push(item);
		});
	}
	
	return jsonEventos;
}