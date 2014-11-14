var margin = {top: 10, right: 40, bottom: 10, left: 40},
    height = 600;


var svg = d3.select("svg")
    .attr({
            "width": "100%",
            "height": height
        })
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var width = $('svg').width();

function get_x(ranking) {
    var y = get_y(ranking) + 1;
    return (ranking - y*(y-1)/2) - 1 + 10 - 0.5*y;
}

function get_y(ranking) {
    var k = Math.floor(Math.sqrt(2*ranking));
    while ((k*(k-1)/2) < ranking) {
        k++;
    }
    while ((k*(k-1)/2) >= ranking) {
        k--;
    }
    return k-1;
}

function get_title(d) {
    return d.name + " (" + d.ranking + "), " + d.country;
}

// http://www.rolandgarros.com/images/misc/masthead_logo.jpg
// http://www.wimbledon.com/images/misc/header_wimlogo.png

var in_format = d3.time.format("%d.%m.%Y");
var key_format = d3.time.format("%Y%m%d");
var hr_format = d3.time.format("%d/%m/%Y");

var x = d3.scale.linear()
    .domain([0,20])
    .range([0, width - margin.left - margin.right]);

var y = d3.scale.linear()
    .domain([0,10])
    .range([0, height - margin.top - margin.bottom]);

function highlight_country(element) {
    svg.selectAll("image")
        .transition()
        .duration(1500)
        .attr({
            "opacity": function(d) { return (d.country == element.__data__.country) ? 1 : 0.1; }
        })
        .transition()
        .duration(3000)
        .attr({
            "opacity": 1
        });
}

function draw_viz(flags, data) {
    var images = svg.selectAll("image")
        //.data(data.get(this.value), function(d) { return d.name; });
        .data(data, function(d) { return d.name; });
    images.select("title").text(function(d) { return get_title(d); });
    images.transition()
        .transition()
        .attr("opacity", 1)
        .duration(1500)
        .attr({
            "x": function(d) { return x(get_x(d.ranking)); },
            "y": function(d) { return y(get_y(d.ranking)); }
        });
    var new_images = images.enter()
        .append("image")
        .attr({
            "xlink:href": function(d) { return flags.has(d.country) ? flags.get(d.country)[0].url : flags.get("PIR")[0].url; },
            "x": function(d) { return x(get_x(d.ranking)); },
            "y": function(d) { return y(get_y(d.ranking)); },
            "width": 40,
            "height": 28,
            "preserveAspectRatio": "none",
            "opacity": 0
        });
    new_images
        .on("click", function() {
            highlight_country(this);
        })
        .on("dblclick", function() {
                window.open(this.__data__.url);
        })
        .append("title").text(function(d) { return get_title(d);});
    new_images.transition().duration(1500).attr('opacity', 1);
    images.exit().remove();
}

var flags;

queue()
    .defer(function(callback) {
        // http://en.wikipedia.org/wiki/List_of_IOC_country_codes
        d3.csv("ioc_flags.csv", function(errors, csv) {
            flags = d3.nest()
                .key(function(d) {return d.code;})
                .map(csv, d3.map);

            callback(null, flags)
        });
    })
    .defer(function(callback) {
        d3.csv("atp_men_singles_ranking.min.csv", function(errors, csv) {
            csv.forEach(function(line) {
                line.ranking = parseInt(line.ranking);
                line.date = in_format.parse(line.date);
                line.url = "http://www.atpworldtour.com" + line.url;
                //line.points = parseInt(line.points.replace(",", ""));
                line.tournaments = parseInt(line.tournaments);
            });

            var data = d3.nest()
            .key(function(d) {return key_format(d.date);})
            .sortKeys(d3.descending)
            .sortValues(function(a,b) { return a.ranking - b.ranking; })
            .map(csv, d3.map);

            var entries = d3.nest()
            .key(function(d) {return key_format(d.date);})
            .rollup(function(leaves) { return leaves.length; })
            .entries(csv);

            callback(null, {
                'data': data,
                'entries' : entries
            });
        });
    })
    .await(function(error, flags, results) {
        var data = results['data'], entries = results['entries'];

        d3.select("select").selectAll("option")
            .data(entries)
            .enter()
            .append("option")
            .attr("value", function (d) {
                return d.key;
            })
            .text(function (d) {
                return hr_format(key_format.parse(d.key));
            })
            .filter(function (d) {
                return d.values < 500
            })
            .remove();

        draw_viz(flags, data.get(data.keys()[0]));
    });

queue()
    .defer(function(callback) {
        d3.csv("atp_men_singles_ranking.csv", function (errors, csv) {
            csv.forEach(function (line) {
                line.ranking = parseInt(line.ranking);
                line.date = in_format.parse(line.date);
                line.url = "http://www.atpworldtour.com" + line.url;
                //line.points = parseInt(line.points.replace(",", ""));
                line.tournaments = parseInt(line.tournaments);
            });

            var data = d3.nest()
            .key(function(d) {return key_format(d.date);})
            .sortKeys(d3.descending)
            .sortValues(function(a,b) { return a.ranking - b.ranking; })
            .map(csv, d3.map);

            var entries = d3.nest()
            .key(function(d) {return key_format(d.date);})
            .rollup(function(leaves) { return leaves.length; })
            .entries(csv);

            callback(null, {
                'data': data,
                'entries' : entries
            });
        })
    })
    .await(function(error, results) {
        var data = results['data'], entries = results['entries'];
        d3.select("select").selectAll("option")
                       .data(entries)
                     .enter()
                       .append("option")
                       .attr("value", function(d) {return d.key;})
                       .text(function(d) {return hr_format(key_format.parse(d.key));})
                       .filter(function(d) { return d.values < 500 })
                       .remove();

        d3.select("select").on("change", function() {
            draw_viz(flags, data.get(this.value));
        });
    });
