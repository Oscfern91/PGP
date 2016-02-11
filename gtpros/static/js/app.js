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

function get_events(proyecto, eventos) {
	
	
	var jsonEventos = [];
	
	if(eventos !== null && eventos.length > 0) {
		var jsonActividades = JSON.parse(eventos);
		$.each(jsonActividades, function(index, evento) {
			var item = {};
			item["id"] = evento.id;
			item["title"] = evento.nombre;
			item["url"] = "/project/".concat(proyecto).concat("/event_popup/").concat(evento.id);
			
			if(evento.duracion == 0)
				item["class"] = "event-special";
			else
				item["class"] = "event-warning";
			var iniDate = new Date(evento.fecha_inicio);
			item["start"] = "".concat(iniDate.getTime());
			var endDate = new Date(evento.fecha_fin);
			item["end"] = "".concat(endDate.getTime());
			
			jsonEventos.push(item);
		});
	}
	
	return jsonEventos;
}