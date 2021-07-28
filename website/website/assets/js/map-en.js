// all references to gP are currently outcommented.
// they refer to the getPDF button which will be implemented later.

function fetch_regions_from_server() {
	return fetch('assets/data/regions.geojson')
}

function fetch_regions_from_api() {
    // TODO: Add cache functionality
    return fetch(apiUrl + '/list_regions')
}

function status(response) {
    if (response.status === 404) {
        console.log('Could not find regions.geojson on the server. Status Code: ' + response.status); 
        console.log('Fetch regions from OQT API. This takes quite a while.');
        return Promise.resolve(fetch_regions_from_api())
    } else {
        return Promise.resolve(response)
    }
}

function json(response) {
    return response.json();
}

// load geojson data, then build the map and the functionalities
Promise.all([
    fetch_regions_from_server()
        .then(status)
        .then(json),
    get_html_parameter_list(location.search)
])
    .then(buildMap)
    .catch(function(error) {
        console.error(error)
    });

var selectedFeature = null;
var selectedFeatureLayer = null;

// Create base map, the layers, the legend and the info text
function buildMap(...charts){
    html_params = charts[0][1]
	// create base map, location and zoom
	map = L.map( 'map', {
	  center: [31.4, -5],
	  minZoom: 2,
	  zoom: 2
	})

	// add references on the bottom of the map
	L.tileLayer( 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
	  subdomains: ['a', 'b', 'c']
	}).addTo( map )

	
// add base layers
	let markers = {}
	world = L.geoJson(charts[0][0], {
		style: {
			fillColor:"#EEF200",  // yellow
			weight: 2,
			opacity: 1,
			color: 'white',
			dashArray: '3',
			fillOpacity: 0.7
			},
		onEachFeature: function onEachFeature(feature, layer) {
			layer.on({
				mouseover: highlightFeature,
				mouseout: resetHighlight,
				click: selectStyle
			});
			
			// Get bounds of polygon
			var bounds = layer.getBounds();
			// Get center of bounds
			var center = bounds.getCenter();
			// Use center to put marker on map
			var marker = L.marker(center).on('click', ()=>{
				map.fitBounds(bounds)
			}).addTo(map);
			let id = feature.id
			markers[id] = marker
			marker.on('click', function(){layer.fire('click')})
		}

	}).addTo(map);

	//Next we’ll define what happens on mouseover:
	function highlightFeature(e) {
		var layer = e.target;

		layer.setStyle({
			weight: 5,
			color: '#666',
			dashArray: '',
			fillOpacity: 0.7
		});

		if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
			layer.bringToFront();
		}
		 info.updateInfo(layer.feature.id);
	}

	//Next we’ll define what happens on mouseout:
	function resetHighlight(e) {
		if(map.hasLayer(world)){
			world.resetStyle(e.target);
		}
		
		info.updateAfter();
	}

	/*The handy geojson.resetStyle method will reset the layer style to its default state 
	(defined by our style function). For this to work, make sure our GeoJSON layer is accessible 
	through the geojson variable by defining it before our listeners and assigning the layer to it later:'*/

	// what happens whlie onclick on the map
	function selectStyle(e) {
		// change value of mapCheck in html to signalize intern area was selected
		update_url("id", e.target.feature.id)
		var s = document.getElementById("mapCheck");
		s.innerHTML = "selected";
		// TODO style selected id
		// alert("I will be red");
		var layer = e.target;
		// get selected feature
		selectedFeature = layer.feature
		if(selectedFeatureLayer)
			map.removeLayer(selectedFeatureLayer)
		selectedFeatureLayer = L.geoJSON(selectedFeature, {
			style: function (feature) {
					return {
						color: 'red',
						fillColor: '#f03',
						fillOpacity: 0.5
					};
			}
		}).addTo(map);

		featureId = layer.feature.id;
		selectedId = featureId
		
		// get dataset ID
		//dataset = layer.feature.properties.featurecla; // = Admin-0 country
		dataset = "regions" // = Admin-0 country
		selectedDataset = dataset
	}
	// initialize variables for storing area and dataset id from map geojson 
	if (html_params["id"] != undefined){
		featureId = parseInt(html_params["id"])
	}
	else {
		featureId = null; 
	}
	selectedId = null;
	selectedDataset = "regions";

	// create a parameter string containing selected area, report and dataset id
	function getParams(region, report, dataset) {
		paramString = region + "," + report + "," + dataset
		return paramString
	}

	function toggle_results_will_be_shown_paragraph(bool){
		var a = document.getElementById("results1");
		var b = document.getElementById("results2");

		if (bool == true) {
			a.style.display = "block";
			b.style.display = "block";
			b.style.marginBottom = "500px";

		} else {
			a.style.display = "none";
			b.style.display = "none";
		}
	}
	
	// ###############   get quality button ###########
	document.getElementById("gQ").onclick = function () { 
		html_params = get_html_parameter_list(location.search)
		var report = document.getElementById("cardtype");

		if(html_params["id"]!=undefined){
			var areas = parseInt(html_params["id"])
		}
		else{
			var areas = document.getElementById("mapCheck").innerHTML;
		}

		if (html_params["report"]!=undefined&report_isValid(html_params["report"])){
			var selectedReport = html_params["report"]
			report.value = selectedReport		
		}
		else{
			var selectedReport = report.options[report.selectedIndex].value;
		}
		if ((areas == "id") | !id_isValid(areas, charts[0][0].features)){
			alert("Please select a region");
		}
		else if (selectedReport == "Report" | !report_isValid(selectedReport)) {		
			alert("Please select a Report");
		}
		else {
			markers[areas].fire("click")
			toggle_results_will_be_shown_paragraph(true)
			// show loader spinner
			document.querySelector("#loader1").classList.add("spinner-1");
			document.querySelector("#loader2").classList.add("spinner-1");
			// remove dynamically created Indicator divs
			removeIndicators()
			// remove selected feature from map
			if(selectedFeatureLayer) map.removeLayer(selectedFeatureLayer)


			var params = {
			    "dataset": String(selectedDataset),
			    "featureId": String(areas)
			}
			console.log(params)
			httpPostAsync(selectedReport, JSON.stringify(params), handleGetQuality);
		 }
		// when params were send, get pdf button turns blue
		changeColor() 
	}; // getQuality Button click ends
	
	function handleGetQuality(response) {
		console.log("response",response)
		toggle_results_will_be_shown_paragraph(false)
		document.querySelector("#loader1").classList.remove("spinner-1");
		document.querySelector("#loader2").classList.remove("spinner-1");

		// show selected region on a map
		addMiniMap();
		// 1=green, 2=yellow, 3=red
		switch (response.result.label) {
		    case 'green':
		        traffic_lights = '<span class="dot-green"></span> <span class="dot"></span> <span class="dot"></span> Good Quality'
		        break
		    case 'yellow':
		        traffic_lights = '<span class="dot"></span> <span class="dot-yellow"></span> <span class="dot"></span> Medium Quality'
		        break
		    case 'red':
		        traffic_lights = '<span class="dot"></span> <span class="dot"></span> <span class="dot-red"></span> Bad Quality'
		}

        document.getElementById("traffic_dots_space").innerHTML =
		            '<h4>Report: '+ response.metadata.name + '</h4>' +
		            '<p>' + traffic_lights + '</p>'
                    // here place to display the name of the region?


		// ' <b>Overall value: '+ response.result.value + '</b></p>'


		document.getElementById("traffic_text_space").innerHTML = '<p>'+ response.result.description +'</p>'
		document.getElementById("report_metadata_space").innerHTML =
		    '<p class="metadata-text">Report description:</br>'+ response.metadata.description +'</p>'
			
		if(Object.keys(response.indicators).length > 0) {
			addIndicators(response.indicators)
		}
		var element = document.getElementById('result-heading');
		var headerOffset = 70;
		var elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
		var offsetPosition = elementPosition - headerOffset;
	
		window.scrollTo({
			 top: offsetPosition,
			 behavior: "smooth"
		});
	}

	/**
	 * Adds indicator by creating div on DOM dynamically based on number of Indicators present
	 * 
	 * @param indicators is an array of indicator
	 */
	function addIndicators(indicators) {
		// console.log('indicators ', indicators)
		var parentDiv = document.getElementById("indicatorSpace");
		// loop throw all indicators and add to DOM
    for (var key in indicators) {
			// console.log('indicator = ', indicator)
			var sectionDiv = document.createElement("div");
			sectionDiv.className = "section-container section-flex"

			// left part with plot
			var left_space = document.createElement("div");
			left_space.classList.add("one-third")
			if (indicators[key].result.label == 'UNDEFINED'){
			    left_space.innerHTML = "<p>Plot can't be calculated for this indicator.</p>";
			} else {
			    left_space.innerHTML = indicators[key].result.svg;
			    left_space.classList.add("indicator-graph");
			}
			sectionDiv.appendChild(left_space)

			// right part with heading, description and traffic lights
			var right_space = document.createElement("div");
			right_space.className = "two-thirds";

			var indicatorHeading = document.createElement("h4");
			indicatorHeading.innerHTML = indicators[key].metadata.name + ' for ' + indicators[key].layer.name ;
			right_space.appendChild(indicatorHeading);

			var indicatorQuality = document.createElement("p");
			switch (indicators[key].result.label) {
                case "green":
                case "1":
                    traffic_lights_indicator = '<p><span class="dot-green"></span> <span class="dot"></span> <span class="dot"></span> Good Quality</p>'
                    break
                case "yellow":
                case "2":
                    traffic_lights_indicator = '<p><span class="dot"></span> <span class="dot-yellow"></span> <span class="dot"></span> Medium Quality</p>'
                    break
                case "red":
                case "3":
                    traffic_lights_indicator = '<p><span class="dot"></span> <span class="dot"></span> <span class="dot-red"></span> Bad Quality</p>'
                    break
                case "undefinied":
                    traffic_lights_indicator = '<p><span class="dot"></span> <span class="dot"></span> <span class="dot"></span> Undefined Quality</p>'
                default:
                    traffic_lights_indicator = '<p><span class="dot"></span> <span class="dot"></span> <span class="dot"></span> Undefined Quality</p>'

            }
            indicatorQuality.innerHTML = traffic_lights_indicator;
            right_space.appendChild(indicatorQuality);

			var indicatorText = document.createElement("p");
			indicatorText.innerHTML = indicators[key].result.description;
			right_space.appendChild(indicatorText);

			var indicatorDescription = document.createElement("p");
			indicatorDescription.className = "metadata-text"
		    indicatorDescription.innerHTML = 'Indicator description:</br>' + indicators[key].metadata.description;
			right_space.appendChild(indicatorDescription);

            sectionDiv.appendChild(right_space)
			parentDiv.appendChild(sectionDiv);

			var horizontalLine = document.createElement("hr")
			horizontalLine.className = "splitline"
			parentDiv.appendChild(horizontalLine);
		};
	}

	/**
	 * Removes the dynamically created Indicator divs
	 */
	function removeIndicators() {
		// clear overall results
		//document.getElementById("trafficTop").innerHTML = '';
		document.getElementById("traffic_map_space").innerHTML = ''
		document.getElementById("traffic_dots_space").innerHTML = ''
		document.getElementById("traffic_text_space").innerHTML = ''
		document.getElementById("report_metadata_space").innerHTML = ''
		//document.getElementById("graphTop").innerHTML = ''

		var parentDiv = document.getElementById("indicatorSpace");
		while (parentDiv.firstChild) {
			//The list is LIVE so it will re-index each call
			parentDiv.removeChild(parentDiv.firstChild);
		}
	}

	/**
	 * Adds a small map to show the selected region
	 */
	function addMiniMap() {
		document.getElementById('traffic_map_space').innerHTML = "<div id='miniMap' class='miniMap' style='width: 90%; height: 100%;'></div>";
		var miniMap = L.map( 'miniMap', {
			center: [31.4, -5],
			zoomControl: false,
			minZoom: 2,
			zoom: 2
		})

		// add references on the bottom of the map
		L.tileLayer( 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | ',
			subdomains: ['a', 'b', 'c']
		}).addTo( miniMap )

		var selectedFeatureLayer = L.geoJSON(selectedFeature, {
			style: function (feature) {
					return {
						color: 'red',
						fillColor: '#f03',
						fillOpacity: 0.5
					};
			}
		}).addTo(miniMap);

		miniMap.fitBounds(selectedFeatureLayer.getBounds());
	}

	// while clicking on the get quality button check for selections -> see changeColorQ()
	document.getElementById("cardtype").onchange = function () {
		changeColorQ()
	} ;
	document.getElementById("map").onclick = function () {
		changeColorQ()
	} ;

	// function to style the get quality button depending on selections
	function changeColorQ() {
		var report = document.getElementById("cardtype");
		var areas = document.getElementById("mapCheck").innerHTML;
		var div = document.getElementById('gQ');
		var selectedReport = report.options[report.selectedIndex].value;
		update_url("report", selectedReport)
		// no selection of area so set buttons to grey
		if (areas == "id") {
			//var divGP = document.getElementById('gP');
			//divGP.style.backgroundColor = 'grey';
			//divGP.className = "btn-report2";
			document.getElementById("gQ").className = "btn-submit2";
		}
	    // no selection of report so set buttons to grey
		if (selectedReport == "Report") {
			//var divGP = document.getElementById('gP');
			//divGP.style.backgroundColor = 'grey';
			//divGP.className = "btn-report2";
			document.getElementById("gQ").className = "btn-submit2";
		}
	    // selection made. set color to blue
		else {
			div.style.backgroundColor = '#535C69';
			div.className = "btn-submit"
		}
	}
	// #################    PDF button #############
	function changeColor() {
		var ifQ = document.getElementById("gQ").className
		//var divGP = document.getElementById('gP');
		if (ifQ == "btn-submit") {
			
			//divGP.style.backgroundColor = '#535C69';
			//divGP.className = "btn-report";

		}
	}
	/*function colorReport() {
		var ifQ = document.getElementById("gQ").className
		var divGP = document.getElementById('gP');

		if (divGP.className == "btn-report") {

			alert("pdf")
		}
		else {
			alert("Please click on the Get Quality button first")
		}
	}
	document.getElementById("gP").onclick = function () {
		colorReport()

	} ;*/

	//This makes the states highlight nicely on hover and gives us the ability to add other interactions inside our listeners.
	/*We could use the usual popups on click to show information about different states, but we’ll choose a
	different route — showing it on state hover inside a custom control.*/
	var info = L.control();

	info.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
		this.updateAfter();
		return this._div;
	};


	// method that we will use to update the info box based on feature properties passed
	info.updateInfo = function (id) {
		// depending on selected layer, show corresponding information
		if(map.hasLayer(world)){
			this._div.innerHTML = '<h5>Click to select</h5>' +  (id ?
				'<p><b>Feature ID: ' + id + '</b>'
				: '<p>Move the mouse over the map</p>'
					);
		}

	};

	// Text showing in info box after mouseover
	info.updateAfter = function () {
		// depending on selected layer, show corresponding information
		if(map.hasLayer(world)) {
			this._div.innerHTML =
			'<p>Move the mouse over the map</p>';
		}

	};


	info.addTo(map);
	// add HeiGIT logo


	if ((report_isValid(html_params["report"]) & id_isValid(featureId, charts[0][0].features))){
		markers[featureId].fire("click")
		document.getElementById("gQ").click()
	}

 }
 function topFunction() {
	document.body.scrollTop = 0; // Sollte für Safari, aber ich habe keinen Mac und ich habe es nicht getestet
	document.documentElement.scrollTop = 0; // Für Chrome, Firefox, IE and Opera
}
function bottomFunction() {
	window.scrollTo(0, document.body.scrollHeight);
}

function httpGetAsync(theUrl, callback)
{
	var xmlHttp = new XMLHttpRequest();
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
			callback(xmlHttp.responseText);
	}
	console.log(theUrl)
	xmlHttp.open("GET", theUrl, true); // true for asynchronous
	xmlHttp.send(null);
	// console.log(xmlHttp.responseText)
	// return xmlHttp.responseText;
}

function httpPostAsync(endPoint, params, callback) {
	var theUrl = apiUrl +"/report/" + endPoint;
	var xmlHttp = new XMLHttpRequest();
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
			callback(JSON.parse(xmlHttp.responseText));
		if (xmlHttp.readyState == 4 && xmlHttp.status !== 200) {
			httpErrorHandle(xmlHttp)
		}
	}
	console.log(theUrl)
	xmlHttp.open("POST", theUrl, true); // true for asynchronous
	xmlHttp.send(params);
}

function getResponseFile( params, callback) {
	var xmlHttp = new XMLHttpRequest();
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
			callback(JSON.parse(xmlHttp.responseText));
	}
	xmlHttp.open("GET", "assets/data/api_response.json", true);
	xmlHttp.send(params);
}

function httpErrorHandle(xmlHttp) {
	console.log('xmlHttp = ', xmlHttp)
	document.querySelector("#loader1").classList.remove("spinner-1");
	document.querySelector("#loader2").classList.remove("spinner-1");
	alert("Error: \n\n"+ xmlHttp.statusText)
}
