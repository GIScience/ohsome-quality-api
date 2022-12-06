// all references to gP are currently outcommented.
// they refer to the getPDF button which will be implemented later.

function fetch_regions_from_server() {
    return fetch("assets/data/regions.geojson");
}

function fetch_report_from_server(reportName, featureId) {
    const fileName = reportName + '-' + featureId + '.json';
    console.log(fileName);
    return fetch("assets/data/" + fileName);
}

function fetch_default_report() {
    return fetch("assets/data/default-report.json");
}

function fetch_regions_from_api() {
    // TODO: Add cache functionality
    return fetch(apiUrl + "/regions?asGeoJSON=True");
}

function status(response) {
    if (response.status === 404) {
        console.log(
            "Could not find regions.geojson on the server. Status Code: " +
                response.status
        );
        console.log("Fetch regions from OQT API. This takes quite a while.");
        return Promise.resolve(fetch_regions_from_api());
    } else {
        return Promise.resolve(response);
    }
}

function reportStatus(response) {
    if (response.status === 404) {
        console.log(
            "Could not find report on the server. Status Code: " +
                response.status
        );
        console.log("Fetch default report.");
        return Promise.resolve(fetch_default_report());
    } else {
        return Promise.resolve(response);
    }
}

function json(response) {
    return response.json();
}

// load geojson data, then build the map and the functionalities
Promise.all([
    fetch_regions_from_server().then(status).then(json),
    get_html_parameter_list(location.search),
])
    .then(buildMap)
    .catch(function (error) {
        console.error(error);
    });

let selectedFeature = null;
let selectedFeatureLayer = null;

// Create base map, the layers, the legend and the info text
function buildMap(...charts) {
    let html_params = charts[0][1];
    // create base map, location and zoom
    let map = L.map("map", {
        center: [31.4, -5],
        minZoom: 2,
        zoom: 2,
    });

    // add references on the bottom of the map
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        subdomains: ["a", "b", "c"],
    }).addTo(map);

    // add base layers
    let markers = {};
    const world = L.geoJson(charts[0][0], {
        style: {
            fillColor: "#EEF200", // yellow
            weight: 2,
            opacity: 1,
            color: "white",
            dashArray: "3",
            fillOpacity: 0.7,
        },
        onEachFeature: function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: selectStyle,
            });

            // Get bounds of polygon
            const bounds = layer.getBounds();
            // Get center of bounds
            const center = bounds.getCenter();
            // Use center to put marker on map
            const marker = L.marker(center)
                .on("click", () => {
                    map.fitBounds(bounds);
                })
                .addTo(map);
            const id = feature.id;
            markers[id] = marker;
            marker.on("click", function () {
                layer.fire("click");
            });
        },
    }).addTo(map);

    // Next we’ll define what happens on mouseover:
    function highlightFeature(e) {
        const layer = e.target;

        layer.setStyle({
            weight: 5,
            color: "#666",
            dashArray: "",
            fillOpacity: 0.7,
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
        update_url("id", e.target.feature.id);
        const s = document.getElementById("mapCheck");
        s.innerHTML = "selected";
        // TODO style selected id
        // alert("I will be red");
        const layer = e.target;
        // get selected feature
        selectedFeature = layer.feature;
        if (selectedFeatureLayer) map.removeLayer(selectedFeatureLayer);
        selectedFeatureLayer = L.geoJSON(selectedFeature, {
            style: function (feature) {
                return {
                    color: "red",
                    fillColor: "#f03",
                    fillOpacity: 0.5,
                };
            },
        }).addTo(map);

        featureId = layer.feature.id;
        selectedId = featureId;

        // get dataset ID
        selectedDataset = "regions";
    }
    // initialize variables for storing area and dataset id from map geojson
    if (html_params["id"] !== undefined) {
        featureId = parseInt(html_params["id"]);
    } else {
        featureId = null;
    }
    selectedDataset = "regions";

    // create a parameter string containing selected area, report and dataset id
    function getParams(region, report, dataset) {
        return region + "," + report + "," + dataset;
    }

    // ###############   get quality button ###########
    document.getElementById("gQ").onclick = function () {
        html_params = get_html_parameter_list(location.search);
        const report = document.getElementById("cardtype");

        let areas;
        if (html_params["id"] !== undefined) {
            areas = parseInt(html_params["id"]);
        } else {
            areas = document.getElementById("mapCheck").innerHTML;
        }

        let selectedReport;
        if (
            html_params["report"] !== undefined &&
            report_isValid(html_params["report"])
        ) {
            selectedReport = html_params["report"];
            report.value = selectedReport;
        } else {
            selectedReport = report.options[report.selectedIndex].value;
        }
        if (areas === "id" || !id_isValid(areas, charts[0][0].features)) {
            alert("Please select a region");
        } else if (
            selectedReport === "Report" ||
            !report_isValid(selectedReport)
        ) {
            alert("Please select a Report");
        } else {
            markers[areas].fire("click");
            // show loader spinner
            document.querySelector("#loader1").classList.add("spinner-1");
            // remove selected feature from map
            if (selectedFeatureLayer) map.removeLayer(selectedFeatureLayer);
            const params = {
                name: String(selectedReport),
                dataset: String(selectedDataset),
                featureId: String(areas),
                includeSvg: true,
                includeHtml: true,
            };
            console.log(params);

            // httpPostAsync(JSON.stringify(params), handleGetQuality);

            Promise.all([fetch_report_from_server(String(selectedReport), String(areas)).then(reportStatus).then(json).then(handleGetQuality)]);
        }
        // when params were sent, get pdf button turns blue
        changeColor();
    }; // getQuality Button click ends

    function handleGetQuality(response) {
        console.log("response", response);
        const properties = response["properties"];
        const report = properties["report"];
        document.getElementById("resultSection").innerHTML = "";
        document.querySelector("#loader1").classList.remove("spinner-1");
        if (report["result"]["html"]) {
            document
                .getElementById("resultSection")
                .insertAdjacentHTML("afterbegin", report["result"]["html"]);
            addMiniMap();
        } else {
            alert("Couldn't create report.");
        }
    }

    /**
     * Adds a small map to show the selected region
     */
    function addMiniMap() {
        document
            .getElementById("report_space")
            .insertAdjacentHTML(
                "afterbegin",
                "<div id='traffic_map_space' style='height: 250px; width: 250px; padding: 10px;'>"
            );
        document
            .getElementById("traffic_map_space")
            .insertAdjacentHTML(
                "afterbegin",
                "<div id='miniMap' class='miniMap' style='width: 90%; height: 100%;'></div>"
            );
        const miniMap = L.map("miniMap", {
            center: [31.4, -5],
            zoomControl: false,
            minZoom: 2,
            zoom: 2,
        });

        // add references on the bottom of the map
        L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | ',
            subdomains: ["a", "b", "c"],
        }).addTo(miniMap);

        selectedFeatureLayer = L.geoJSON(selectedFeature, {
            style: function (feature) {
                return {
                    color: "red",
                    fillColor: "#f03",
                    fillOpacity: 0.5,
                };
            },
        }).addTo(miniMap);

        miniMap.fitBounds(selectedFeatureLayer.getBounds());
    }

    // while clicking on the get quality button check for selections -> see changeColorQ()
    document.getElementById("cardtype").onchange = function () {
        changeColorQ();
    };
    document.getElementById("map").onclick = function () {
        changeColorQ();
    };

    // function to style the get quality button depending on selections
    function changeColorQ() {
        const report = document.getElementById("cardtype");
        const areas = document.getElementById("mapCheck").innerHTML;
        const div = document.getElementById("gQ");
        const selectedReport = report.options[report.selectedIndex].value;
        update_url("report", selectedReport);
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
            div.style.backgroundColor = "#535C69";
            div.className = "btn-submit";
        }
    }
    // #################    PDF button #############
    function changeColor() {
        const ifQ = document.getElementById("gQ").className;
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
        this._div = L.DomUtil.create("div", "info"); // create a div with a class "info"
        this.updateAfter();
        return this._div;
    };

    // method that we will use to update the info box based on feature properties passed
    info.updateInfo = function (id) {
        // depending on selected layer, show corresponding information
        if (map.hasLayer(world)) {
            this._div.innerHTML =
                "<h5>Click to select</h5>" +
                (id
                    ? "<p><b>Feature ID: " + id + "</b>"
                    : "<p>Move the mouse over the map</p>");
        }
    };

    // Text showing in info box after mouseover
    info.updateAfter = function () {
        // depending on selected layer, show corresponding information
        if (map.hasLayer(world)) {
            this._div.innerHTML = "<p>Move the mouse over the map</p>";
        }
    };

    info.addTo(map);
    // add HeiGIT logo

    if (
        report_isValid(html_params["report"]) &&
        id_isValid(featureId, charts[0][0].features)
    ) {
        markers[featureId].fire("click");
        document.getElementById("gQ").click();
    }
}
function topFunction() {
    document.body.scrollTop = 0; // Sollte für Safari, aber ich habe keinen Mac und ich habe es nicht getestet
    document.documentElement.scrollTop = 0; // Für Chrome, Firefox, IE and Opera
}
function bottomFunction() {
    window.scrollTo(0, document.body.scrollHeight);
}

function httpGetAsync(theUrl, callback) {
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            callback(xmlHttp.responseText);
    };
    console.log(theUrl);
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
    // console.log(xmlHttp.responseText)
    // return xmlHttp.responseText;
}

function httpPostAsync(params, callback) {
    const theUrl = apiUrl + "/report";
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            callback(JSON.parse(xmlHttp.responseText));
        if (xmlHttp.readyState === 4 && xmlHttp.status !== 200) {
            httpErrorHandle(xmlHttp);
        }
    };
    console.log(theUrl);
    xmlHttp.open("POST", theUrl, true); // true for asynchronous
    xmlHttp.setRequestHeader("Content-Type", "application/json");
    xmlHttp.send(params);
}

function getResponseFile(params, callback) {
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            callback(JSON.parse(xmlHttp.responseText));
    };
    xmlHttp.open("GET", "assets/data/api_response.json", true);
    xmlHttp.send(params);
}

function httpErrorHandle(xmlHttp) {
    console.log("xmlHttp = ", xmlHttp);
    document.querySelector("#loader1").classList.remove("spinner-1");
    alert("Error: \n\n" + xmlHttp.statusText);
}
