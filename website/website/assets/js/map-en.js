// all references to gP are currently outcommented.
// they refer to the getPDF button which will be implemented later.

// define traffic lights
const GOOD_QUALITY = '<span class="dot-green"></span> <span class="dot"></span> <span class="dot"></span> Good Quality';
const MEDIUM_QUALITY = '<span class="dot"></span> <span class="dot-yellow"></span> <span class="dot"></span> Medium Quality'
const BAD_QUALITY = '<span class="dot"></span> <span class="dot"></span> <span class="dot-red"></span> Bad Quality'
const UNDEFINED_QUALITY = '<span class="dot"></span> <span class="dot"></span> <span class="dot"></span> Undefined Quality'

function fetch_regions_from_server() {
	return fetch('assets/data/regions.geojson')
}

function fetch_regions_from_api() {
    // TODO: Add cache functionality
    return fetch(apiUrl + '/regions')
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

let selectedFeature = null;
let selectedFeatureLayer = null;

// Create base map, the layers, the legend and the info text
function buildMap(...charts){
    let html_params = charts[0][1]
	// create base map, location and zoom
	let map = L.map( 'map', {
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
	const world = L.geoJson(charts[0][0], {
		style: {
			fillColor: "#EEF200",  // yellow
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
			const bounds = layer.getBounds();
			// Get center of bounds
			const center = bounds.getCenter();
			// Use center to put marker on map
			const marker = L.marker(center).on('click', () => {
				map.fitBounds(bounds)
			}).addTo(map);
			const id = feature.id
			markers[id] = marker
			marker.on('click', function () {
				layer.fire('click')
			})
		}

	}).addTo(map);

	// Next we’ll define what happens on mouseover:
	function highlightFeature(e) {
		const layer = e.target;

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

	// Next we’ll define what happens on mouseout:
	function resetHighlight(e) {
		if (map.hasLayer(world)) {
			world.resetStyle(e.target);
		}
		
		info.updateAfter();
	}

	/*The handy geojson.resetStyle method will reset the layer style to its default state 
	(defined by our style function). For this to work, make sure our GeoJSON layer is accessible 
	through the geojson variable by defining it before our listeners and assigning the layer to it later:'*/

	let selectedDataset, featureId, selectedId;
	// what happens while onclick on the map
	function selectStyle(e) {
		// change value of mapCheck in html to signalize intern area was selected
		update_url("id", e.target.feature.id)
		const s = document.getElementById("mapCheck");
		s.innerHTML = "selected";
		// TODO style selected id
		// alert("I will be red");
		const layer = e.target;
		// get selected feature
		selectedFeature = layer.feature
		if (selectedFeatureLayer) map.removeLayer(selectedFeatureLayer)
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
		selectedDataset = "regions"
	}
	// initialize variables for storing area and dataset id from map geojson 
	if (html_params["id"] !== undefined) {
		featureId = parseInt(html_params["id"])
	}
	else {
		featureId = null; 
	}
	selectedDataset = "regions";

	// create a parameter string containing selected area, report and dataset id
	function getParams(region, report, dataset) {
		return region + "," + report + "," + dataset
	}

	function toggle_results_will_be_shown_paragraph(bool) {
		const a = document.getElementById("results1");
		const b = document.getElementById("results2");

		if (bool === true) {
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
		const report = document.getElementById("cardtype");

		let areas;
		if (html_params["id"] !== undefined) {
			areas = parseInt(html_params["id"])
		} else {
			areas = document.getElementById("mapCheck").innerHTML;
		}

		let selectedReport;
		if (html_params["report"] !== undefined && report_isValid(html_params["report"])){
			selectedReport = html_params["report"]
			report.value = selectedReport		
		} else {
			selectedReport = report.options[report.selectedIndex].value;
		}
		if ((areas === "id") || !id_isValid(areas, charts[0][0].features)){
			alert("Please select a region");
		} else if (selectedReport === "Report" || !report_isValid(selectedReport)) {
			alert("Please select a Report");
		} else {
			markers[areas].fire("click")
			toggle_results_will_be_shown_paragraph(true)
			// show loader spinner
			document.querySelector("#loader1").classList.add("spinner-1");
			document.querySelector("#loader2").classList.add("spinner-1");
			// remove dynamically created Indicator divs
			removeIndicators()
			// remove selected feature from map
			if(selectedFeatureLayer) map.removeLayer(selectedFeatureLayer)


			const params = {
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
		const properties = unflattenObject(response["properties"]);
		const report = properties["report"];
		const indicators = properties["indicators"];
		toggle_results_will_be_shown_paragraph(false)
		document.querySelector("#loader1").classList.remove("spinner-1");
		document.querySelector("#loader2").classList.remove("spinner-1");

		// show selected region on a map
		addMiniMap();
		// 1=green, 2=yellow, 3=red
		let traffic_lights;
		switch (report["result"]["label"]) {
		    case 'green':
		        traffic_lights = GOOD_QUALITY;
		        break;
		    case 'yellow':
		        traffic_lights = MEDIUM_QUALITY;
		        break;
		    case 'red':
		        traffic_lights = BAD_QUALITY;
		        break;
		    default:
		        traffic_lights = UNDEFINED_QUALITY;
		        break;
		}

		document.getElementById("traffic_dots_space").innerHTML =
		            '<h4>Report: '+ report["metadata"]["name"] + '</h4>' +
		            '<p>' + traffic_lights + '</p>'
                    // here place to display the name of the region?


		// ' <b>Overall value: '+ response.result.value + '</b></p>'


		document.getElementById("traffic_text_space").innerHTML = '<p>'+ report["result"]["description"] +'</p>'
		document.getElementById("report_metadata_space").innerHTML =
		    '<p class="metadata-text">Report description:</br>'+ report["metadata"]["description"] +'</p>'
			
		if (Object.keys(indicators).length > 0) {
			addIndicators(indicators)
		}
		const element = document.getElementById('result-heading');
		const headerOffset = 70;
		const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
		const offsetPosition = elementPosition - headerOffset;
	
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
		const parentDiv = document.getElementById("indicatorSpace");
		// loop throw all indicators and add to DOM
		for (const idx in indicators) {
			const indicator = indicators[idx];
			// console.log('indicator = ', indicator)
			const sectionDiv = document.createElement("div");
			sectionDiv.className = "section-container section-flex"

			// left part with plot
			const left_space = document.createElement("div");
			left_space.classList.add("one-third")
			if (indicator["result"]["label"] === "UNDEFINED") {
			    left_space.innerHTML = "<p>Plot can't be calculated for this indicator.</p>";
			} else {
			    left_space.innerHTML = indicator["result"]["svg"];
			    left_space.classList.add("indicator-graph");
			}
			sectionDiv.appendChild(left_space)

			// right part with heading, description and traffic lights
			const right_space = document.createElement("div");
			right_space.className = "two-thirds";

			const indicatorHeading = document.createElement("h4");
			indicatorHeading.innerHTML = indicator["metadata"]["name"] + ' for ' + indicator["layer"]["name"];
			right_space.appendChild(indicatorHeading);

			const indicatorQuality = document.createElement("p");
			let traffic_lights_indicator;
			switch (indicator["result"]["label"]) {
                case "green":
                case "1":
                    traffic_lights_indicator = GOOD_QUALITY
                    break
                case "yellow":
                case "2":
                    traffic_lights_indicator = MEDIUM_QUALITY
                    break
                case "red":
                case "3":
                    traffic_lights_indicator = BAD_QUALITY
                    break
                case "undefined":
                    traffic_lights_indicator = UNDEFINED_QUALITY
					break
                default:
                    traffic_lights_indicator = UNDEFINED_QUALITY
					break

            }
            indicatorQuality.innerHTML = '<p>' + traffic_lights_indicator + '</p>';
            right_space.appendChild(indicatorQuality);

			const indicatorText = document.createElement("p");
			indicatorText.innerHTML = indicator["result"]["description"];
			right_space.appendChild(indicatorText);

			const indicatorDescription = document.createElement("p");
			indicatorDescription.className = "metadata-text"
		    indicatorDescription.innerHTML = 'Indicator description:</br>' + indicator["metadata"]["description"];
			right_space.appendChild(indicatorDescription);

            sectionDiv.appendChild(right_space)
			parentDiv.appendChild(sectionDiv);

			const horizontalLine = document.createElement("hr")
			horizontalLine.className = "splitline"
			parentDiv.appendChild(horizontalLine);
		}
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

		const parentDiv = document.getElementById("indicatorSpace");
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
		const miniMap = L.map( 'miniMap', {
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

		selectedFeatureLayer = L.geoJSON(selectedFeature, {
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
		const report = document.getElementById("cardtype");
		const areas = document.getElementById("mapCheck").innerHTML;
		const div = document.getElementById('gQ');
		const selectedReport = report.options[report.selectedIndex].value;
		update_url("report", selectedReport)
		// no selection of area so set buttons to grey
		if (areas === "id") {
			//const divGP = document.getElementById('gP');
			//divGP.style.backgroundColor = 'grey';
			//divGP.className = "btn-report2";
			document.getElementById("gQ").className = "btn-submit2";
		}
	    // no selection of report so set buttons to grey
		if (selectedReport === "Report") {
			//const divGP = document.getElementById('gP');
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
		const ifQ = document.getElementById("gQ").className
		//const divGP = document.getElementById('gP');
		if (ifQ === "btn-submit") {
			
			//divGP.style.backgroundColor = '#535C69';
			//divGP.className = "btn-report";

		}
	}
	/*function colorReport() {
		const ifQ = document.getElementById("gQ").className
		const divGP = document.getElementById('gP');

		if (divGP.className === "btn-report") {

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
	const info = L.control();

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


	if ((report_isValid(html_params["report"]) && id_isValid(featureId, charts[0][0].features))){
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
	const xmlHttp = new XMLHttpRequest();
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
			callback(xmlHttp.responseText);
	}
	console.log(theUrl)
	xmlHttp.open("GET", theUrl, true); // true for asynchronous
	xmlHttp.send(null);
	// console.log(xmlHttp.responseText)
	// return xmlHttp.responseText;
}

function httpPostAsync(endPoint, params, callback) {
	const theUrl = apiUrl + "/report/" + endPoint;
	const xmlHttp = new XMLHttpRequest();
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
			callback(JSON.parse(xmlHttp.responseText));
		if (xmlHttp.readyState === 4 && xmlHttp.status !== 200) {
			httpErrorHandle(xmlHttp)
		}
	}
	console.log(theUrl)
	xmlHttp.open("POST", theUrl, true); // true for asynchronous
	xmlHttp.send(params);
}

function getResponseFile( params, callback) {
	const xmlHttp = new XMLHttpRequest();
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
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
