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

function get_events(proyecto, eventos, informes) {
	
	
	var jsonEventos = [];
	
	if(eventos !== null && eventos.length > 0) {
		var jsonActividades = JSON.parse(eventos);
		$.each(jsonActividades, function(index, evento) {
			var item = {};
			item["id"] = evento.id;
			item["title"] = evento.nombre;
			item["url"] = "/project/".concat(proyecto).concat("/event_popup/").concat(evento.id);
			
			if(evento.duracion == 0)
				item["class"] = "event-info";
			else
				item["class"] = "event-warning";
			var iniDate = new Date(evento.fecha_inicio);
			item["start"] = "".concat(iniDate.getTime());
			var endDate = new Date(evento.fecha_fin);
			item["end"] = "".concat(endDate.getTime());
			
			jsonEventos.push(item);
		});
	}
	
	if(informes !== null && informes.length > 0) {
		var jsonInformes = JSON.parse(informes);
		$.each(jsonInformes, function(index, informe) {
			var item = {};
			item["id"] = informe.id;
			item["title"] = "Informe de la actividad: '".concat(informe.rol__evento__nombre).concat("'");
			item["url"] = "/project/".concat(proyecto).concat("/report_popup/").concat(informe.id);
			
			if(informe.aceptado)
				item["class"] = "event-success";
			else
				item["class"] = "event-important";
			var iniDate = new Date(informe.fecha);
			item["start"] = "".concat(iniDate.getTime());
			var endDate = new Date(informe.fecha);
			item["end"] = "".concat(endDate.getTime());
			
			jsonEventos.push(item);
		});
	}
	
	return jsonEventos;
}