// all references to gP are currently outcommented.
// they refer to the getPDF button which will be implemented later.

// load geojson data, then build the map and the functionalities
Promise.all([
	fetch('assets/data/test_regions.geojson').then(data => data.json()),
]).then(buildMap).catch(err => console.error(err));

var selectedFeature = null;
var selectedFeatureLayer = null;

// If no value is avaiable in the data, there is a -77, return a stripe pattern as color for these ccases
function getStripes(d) {
	if (d == -77){		
		return stripes
	}			   
}

// Set the style for the layers depending on the CO2 values of each layer property
function setStyle(feature) {
		var colorFill = getColor1(feature.properties.geou_dif);

			return {
				fillColor: colorFill,
				fillPattern:getStripes(feature.properties.geou_dif),
				weight: 2,
				opacity: 1,
				color: 'white',
				dashArray: '3',
				fillOpacity: 0.7
			};
		
};

// Function that defines the colors for a value range 
function getColor1(d) {	
	if (d == 0){return 'fff'}
	else {
		return d > 8.0 ? '#4d004b' :
			
			   d > 7.0  ? '#810f7c' :
			   d > 6.0 ? '#88419d' :
			
			   d > 5.0  ? '#8c6bb1' :
			  
			   d > 4.0  ? '#8c96c6' :
			
			   d > 3.0   ? '#9ebcda' :
			   
			   d > 2.0   ? '#bfd3e6' :
			 
			   d > 1.0   ? '#e0ecf4' :
			
			   d > 0.0001   ? '#f7fcfd' :
			   
			   d > 0   ? 'green' :
						  'yellow'
	}
			   
}

// Create base map, the layers, the legend and the info text
function buildMap(...charts){
	
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
	world = L.geoJson(charts[0], {
		style: setStyle,
		onEachFeature: function onEachFeature(feature, layer) {
			layer.on({
				mouseover: highlightFeature,
				mouseout: resetHighlight,
				click: selectStyle
			});
			// display a marker instead of a polygon for test-regions
			if (feature.geometry.type === 'Polygon') {
                // Get bounds of polygon
                var bounds = layer.getBounds();
                // Get center of bounds
                var center = bounds.getCenter();
                // Use center to put marker on map
				var marker = L.marker(center).on('click', zoomToMarker).addTo(map);
				marker.on('click', function(){layer.fire('click')})
            }
            // end add marker for test regions
		}

	}).addTo(map);

    function zoomToMarker(e) {
        map.setView(e.latlng, 10);
    }


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
		 info.updateInfo(layer.feature.properties);
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
		var s = document.getElementById("mapCheck");
		s.innerHTML = "selected";
		// TODO style selected country
		// alert("I will be red");
		var layer = e.target;
		// get selected country
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

		countryID = layer.feature.properties.fid;
		selectedCountry = getCountry(countryID)
		
		// get dataset ID
		//dataset = layer.feature.properties.featurecla; // = Admin-0 country
		dataset = "test_regions" // = Admin-0 country
		selectedDataset = getDataset(dataset)
	}
	// initialize variables for storing area and dataset id from map geojson 
	countryID = null; 
	selectedCountry = null;
	selectedDataset = null;
	// grap country name while clicking on map
	function getCountry(c) {
		// console.log("in getC")
		// console.log(c)
		return c
	}
	// grap dataset id  while clicking on map
	function getDataset(d) {
		console.log("in getD")
		console.log(d)
		return d
	}
	// create a parameter string containing selected area, topic and dataset id
	function getParams(region, topic, dataset) {
		paramString = region + "," + topic + "," + dataset
		return paramString
	}
	
	// ###############   get quality button ###########
	document.getElementById("gQ").onclick = function () { 
		var topic = document.getElementById("cardtype");
		var areas = document.getElementById("mapCheck").innerHTML;

		var selectedTopic = topic.options[topic.selectedIndex].value;
	
		if (areas == "country") {			
			alert("Please select a region");
		}
		else if (selectedTopic == "Topic") {		
			alert("Please select a topic");
		}
		else {
			// show loader spinner
			document.querySelector("#loader1").classList.add("spinner-1");
			document.querySelector("#loader2").classList.add("spinner-1");
			// remove dynamically created Indicator divs
			removeIndicators()
			// remove selected feature from map
			map.removeLayer(selectedFeatureLayer)

			var x = document.getElementById("results1");
			if (x.style.display === "none") {
				x.style.display = "block";
			} else {
				x.style.display = "none";
			}
			var x = document.getElementById("results2");
			if (x.style.display === "none") {
				x.style.display = "block";
			} else {
				x.style.display = "none";
			}

			var params = {
			    "dataset": String(getDataset(selectedDataset)),
			    "featureId": String(getCountry(selectedCountry))
			}
			console.log(params)
			httpPostAsync(selectedTopic, JSON.stringify(params), handleGetQuality);

		}
		// when params were send, get pdf button turns blue
		changeColor() 
	}; // getQuality Button click ends
	
	function handleGetQuality(response) {
		console.log("response",response)
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

		// scroll to results
		document.getElementById('resultSection').scrollIntoView();
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
			horizontalLine.className = "wrapper"
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
	document.getElementById("cardtype").onclick = function () {
		changeColorQ()
	} ;
	document.getElementById("map").onclick = function () {
		changeColorQ()
	} ;

	// function to style the get quality button depending on selections
	function changeColorQ() {
		var topic = document.getElementById("cardtype");
		var areas = document.getElementById("mapCheck").innerHTML;
		var div = document.getElementById('gQ');
		var selectedTopic = topic.options[topic.selectedIndex].value;
		console.log(selectedTopic)
		// no selection of area so set buttons to grey
		if (areas == "country") {
			//var divGP = document.getElementById('gP');
			//divGP.style.backgroundColor = 'grey';
			//divGP.className = "btn-report2";
			document.getElementById("gQ").className = "btn-submit2";
			div.style.backgroundColor = 'grey';
		}
	    // no selection of topic so set buttons to grey
		if (selectedTopic == "Topic") {
			console.log("imhere")
			//var divGP = document.getElementById('gP');
			//divGP.style.backgroundColor = 'grey';
			//divGP.className = "btn-report2";
			document.getElementById("gQ").className = "btn-submit2";
			div.style.backgroundColor = 'grey';
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



	// Text showing in info box before and while selecting a layer
	$('.leaflet-control-layers-selector').click(function(){

		var inside = document.getElementsByClassName("info").item(0);
		// set timeslider to first year (2010)


		if(map.hasLayer(world)) {
			inside.innerHTML = '<p>Move the mouse over the map</p>';
		}			;


	});

	// method that we will use to update the info box based on feature properties passed
	info.updateInfo = function (props) {
		// get CO2 emission value as number from layer properties
		var value = props.fid ;

		// get corresponding year from layer properties

		// depending on selected layer, show corresponding information
		if(map.hasLayer(world)){
			this._div.innerHTML = '<h5>Click to select</h5>' +  (props ?
				'<p><b>Feature ID: ' + props.fid 	+ '</b>'
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

	/*// add a legend to the map
	var legend = L.control({position: 'bottomright'});

	legend.onAdd = function (map) {
		// create a div for the legend with class "info legend"
		var div = L.DomUtil.create('div', 'info legend'),
			grades = [0,1,2,3,4,5,6,7,8],
			labels = [];
		// put color for exactly value 0 in legend
		div.innerHTML +='<p>t CO<sub>2</sub> eq. per capita</p>'
		div.innerHTML +='<p>0 <i style="background:' + getColor1(grades[0]) + '"></i> </p>'
		// loop through our density intervals and generate a label with a colored square for each interval
		for (var i = 0; i < grades.length; i++) {
			div.innerHTML +=
				'<i style="background:' + getColor1(grades[i] + 1) + '"></i> <p>' +
				grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br></p>' : '+</p>');
		}
		div.innerHTML +='<p>Missing values<i class="keinWert" ></i> </p>'
		return div;
	};*/


	info.addTo(map);
	//legend.addTo(map);
	// add HeiGIT logo
	var logo = L.control({ position: 'topleft' });
	logo.onAdd = function (map) {
		  var logoContainer = L.DomUtil.create('div', 'logoContainer')
		  logoContainer.innerHTML = `<div id="support" style="background-color:white"><p>supported by </p>
		  <a  href="https://heigit.org/" target = "_blank"><img src='assets/img/logos/heigit_logo.png'/></a><br>
		  <p>and </p> <a href="https://www.geog.uni-heidelberg.de/gis/index.html" target = "_blank">
		  <img src='assets/img/logos/Logo_UNI_GIScience_HD.png'/></a></div>`
		  return logoContainer
	}
	//logo.addTo(map)

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
