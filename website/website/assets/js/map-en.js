// load geojson data, then build the map and the functionalities 
d3.queue()
  .defer(d3.json, 'assets/data/privHouse.geojson')
  .defer(d3.json, 'assets/data/transport.geojson')
  .defer(d3.json, 'assets/data/industry.geojson')
  .defer(d3.json, 'assets/data/trades.geojson')
  .defer(d3.json, 'assets/data/municipProp.geojson')
  .defer(d3.json, 'assets/data/OSM_landuse_industrial.geojson')
  .defer(d3.json, 'assets/data/OSM_shop_farm.geojson')
  .defer(d3.json, 'assets/data/OSM_landuse_commercial.geojson')
  .defer(d3.json, 'assets/data/custom.geojson')
  .await(buildMap)
  


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
function buildMap(err, ...charts){
	
	// create base map, location and zoom
	map = L.map( 'map', {
	  center: [31.4, -5],
	  minZoom: 2,
	  zoom: 2
	})

	// add references on the bottom of the map
	L.tileLayer( 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | ',
	  subdomains: ['a', 'b', 'c']
	}).addTo( map )

	
// add base layers
	world = L.geoJson(charts[8], {
		
		style: setStyle,
		onEachFeature: function onEachFeature(feature, layer) {
				  
			layer.on({
				mouseover: highlightFeature,
				mouseout: resetHighlight,
				click: selectStyle
		  }
			);
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
		alert("I will be red");
		var layer = e.target;
		// get selected country
		countryID = layer.feature.properties.name;
		selectedCountry = getCountry(countryID)
		
		// get dataset ID
		dataset = layer.feature.properties.featurecla; // = Admin-0 country
		selectedDataset = getDataset(dataset)
	}
	// initialize variables for storing area and dataset id from map geojson 
	countryID = null; 
	selectedCountry = null;
	selectedDataset = null;
	// grap country name while clicking on map
	function getCountry(c) {
		console.log("in getC")
		console.log(c)
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
		// scroll the page a bit up when clicking on the get quality button
		document.querySelector('#results').scrollIntoView({
			behavior: 'smooth'
		});
		// check selections
		var topic = document.getElementById("cardtype");
		var areas = document.getElementById("mapCheck").innerHTML;

		var selectedValue = topic.options[topic.selectedIndex].value;
	
		if (areas == "country") {			
			alert("Please select a region");
		}
		else if (selectedValue == "Topic") {		
			alert("Please select a topic");
		}
		else {
			var x = document.getElementById("results");
			if (x.style.display === "none") {
				x.style.display = "block";
			} else {
				x.style.display = "none";
			}
			// get and send paramater for and to api
			var region = getCountry(selectedCountry)
			var dataset = getDataset(selectedDataset)
			args = getParams(region, selectedValue, dataset);
			console.log(args)
			// put args in url:
			// 	"http://0.0.0.0:8000/indicator/poiDensity/"
			// send Params
			httpGetAsync("https://api.ohsome.org/v1/elements/area?bboxes=8.625%2C49.3711%2C8.7334%2C49.4397&format=json&time=2014-01-01&filter=landuse%3Dfarmland%20and%20type%3Away", 
			
		
			function(response) {
				console.log("response")
				console.log(response)
	
			});

			// ######   traffic  light ########
			document.getElementById("trafficTop").innerHTML = 
			
				 '<h5>Overall quality</h5>';
			document.getElementById("traffic_map_space").innerHTML = 
			
				 '<img src="../assets/img/map.png">';
			document.getElementById("traffic_dots_space").innerHTML = 
			
				 '<img src="../assets/img/ampel.PNG">';
				 
			document.getElementById("traffic_text_space").innerHTML = 
			
				'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore '+    
				'et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.';
			 // ######   graph ########
			document.getElementById("graphTop").innerHTML = 
			
				 '<h5>Stats about traffic light calculation</h5>';
			document.getElementById("graph_space").innerHTML = 
			
				 '<img src="../assets/img/psy.png">';
			document.getElementById("text_space").innerHTML = 
				'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore '+    
				'et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. '+    
				'Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit'+    
				'amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam '+    
				'erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, '+    
				'no sea takimata sanctus est Lorem ipsum dolor sit amet.';
			
			// ######   details ########
			document.getElementById("calcTop").innerHTML = 
			
			'<h5>Indicator calculation explanation</h5>';
			document.getElementById("calc_space").innerHTML = 
				'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore '+    
				'et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. '+    
				'Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit'+    
				'amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam '+    
				'erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, '+    
				'no sea takimata sanctus est Lorem ipsum dolor sit amet.';
    	    // TODO implement nice waiting process delay
			alert('Is prcessing ...!'); 
			
		}
		// when params were send, get pdf button turns blue
		changeColor() 
	};
	
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
		var selectedValue = topic.options[topic.selectedIndex].value;
		console.log(selectedValue)
		// no selection of area so set buttons to grey
		if (areas == "country") {
			var divGP = document.getElementById('gP');
			divGP.style.backgroundColor = 'grey';
			divGP.className = "btn-report2";
			document.getElementById("gQ").className = "btn-submit2";
			div.style.backgroundColor = 'grey';
		}
	    // no selection of topic so set buttons to grey
		if (selectedValue == "Topic") {
			console.log("imhere")
			var divGP = document.getElementById('gP');
			divGP.style.backgroundColor = 'grey';
			divGP.className = "btn-report2";
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
		var divGP = document.getElementById('gP');
		if (ifQ == "btn-submit") {
			
			divGP.style.backgroundColor = '#535C69';
			divGP.className = "btn-report";
		}
	}
	function colorRepoort() {
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
		colorRepoort()
		
	} ;
		
		
		
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
		var value = props.name ;
		
		// get corresponding year from layer properties
		
		// depending on selected layer, show corresponding information
		if(map.hasLayer(world)){
			this._div.innerHTML = '<h5>Click to select</h5>' +  (props ?
				'<p><b>Country: ' + props.name 	+ '</b>'
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

	// add a legend to the map
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
	};


	info.addTo(map);
	legend//.addTo(map);
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
	logo//.addTo(map)

 }
// function to go to the top of page by onclick
function topFunction() {
	document.body.scrollTop = 0; // Sollte für Safari, aber ich habe keinen Mac und ich habe es nicht getestet
	document.documentElement.scrollTop = 0; // Für Chrome, Firefox, IE and Opera
}
// function to go to the bottom of page by onclick
function bottomFunction() {
	window.scrollTo(0, document.body.scrollHeight);
}
// function to send user selection to api
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
	console.log(xmlHttp.responseText)
	return xmlHttp.responseText;
}
