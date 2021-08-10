function get_html_parameter_list(querystring) {
    if (querystring === '') return {};
    const params = querystring.slice(1);
    const pairs = params.split("&");
    const result = {}
    for (const item of pairs) {
      const pair = item.split("=");
      const name = unescape(pair[0]).replace("+", " ");
      const value = unescape(pair[1]).replace("+", " ");
      result[name] = value;
    }
    return result
  }

function update_url(key, value){
    const params = get_html_parameter_list(location.search)
    params[key] = value
    let new_params = "?"
    for (const x of Object.keys(params)) {
        new_params += x + "=" + params[x] + "&"
    }
    new_params = new_params.slice(0,-1)
    window.history.replaceState(null, null, new_params);
}

// check if a report with this name is implemented
function report_isValid(report){
    const valid_options = []
    for (const option of document.getElementById("cardtype").options) {
        valid_options.push(option.value)
      }
    return valid_options.includes(report)
}

// check if test region id is in the test regions file. This functions need to be updated once we have other inputs.
function id_isValid(value, json){
    let valid_options = []
    for (elem of json){
        valid_options.push(elem.id)
    }
    return valid_options.includes(value)
}
