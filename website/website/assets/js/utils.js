function get_html_parameter_list(querystring) {
    if (querystring == '') return {};
    var params = querystring.slice(1);
    var pairs = params.split("&");
    var pair, name, value;
    var result = {}
    for (var i = 0; i < pairs.length; i++) {
      pair = pairs[i].split("=");
      name = pair[0];
      value = pair[1];
      name = unescape(name).replace("+", " ");
      value = unescape(value).replace("+", " ");
      result[name] = value;
    }
    return result
  }

function update_url(key, value){
    let params = get_html_parameter_list(location.search)
    console.log(params)
    params[key]=value
    let new_params = "?"
    for(const x of Object.keys(params)){
        new_params += x + "=" + params[x] + "&"
    }
    new_params = new_params.slice(0,-1)
    window.history.replaceState(null, null, new_params);
}

function topic_isValid(topic){
    let valid_options = []
    for (var option of document.getElementById("cardtype").options) {
        valid_options.push(option.value)
      }
    return valid_options.includes(topic)
}

function country_isValid(value, json){
    let valid_options = []
    for (elem of json){
        valid_options.push(elem.properties.fid)
    }
    return value in valid_options
}
