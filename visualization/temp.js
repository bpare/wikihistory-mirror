// We are using a d3 timeline to display the data in the CSV
//I recommend checking out github.com/denisemauldin/d3-timeline to understand this a bit better

var width = 800;
var height = 50;

//With parseDate, we define what the time data looks like for d3

var parseDate = d3.time.format("%Y-%m-%d").parse;

// read the CSV 
d3.csv("TITLE" + "Total.csv", function(d) {
  return {
  

    times: [{
      "starting_time": parseDate(d.Start).getTime(),
      "ending_time": parseDate(d.End).getTime(),
      "color":(d.Color),
    }], 

  };
}, 

// d is the current rendering object
function(d) {

  //group data by labels
  var k = d3.nest()
    .key(function(d) {
      return d.label;
    }).entries(d);
    
    
  //create array of data with labels and times
  var arr = [];
  k.forEach(function(d) {
    var ob = {};
    ob.times = [];
    arr.push(ob);    
    d.values.forEach(function(v) {
      ob.times.push(v.times)
    });
    ob.times = [].concat.apply([], ob.times);
  });



//create the timeline object

function timelineRect() {
	var formatTime = d3.time.format("%Y-%m-%d");

    var colorScale = d3.scale.ordinal().range(['#ed5565', '#ffce54', '#48cfad', '#5d9cec', '#ec87c0', '#ac92ec', '#4fc1e9', '#fc6e51', '#a0d468', '#656d78'])
    var chart = d3.timeline()
      .colors(colorScale)

	// This links to an article if its data was clicked on the timeline
      .click(function (d, i, datum) {
            time = +d.starting_time; 
            date = new Date(time);
			var url = "_"+"TITLE";
			link_id = formatTime(date);
            url += link_id;
            url += ".html";
        	window.location = url; 
					})
      .colorProperty('event_type')
      .rotateTicks(45)
      .tickFormat({
        format: d3.time.format("%b %Y"),
        tickTime: d3.time.month.day,
        tickInterval: 30,
        tickSize: 5
      })
      .stack();


    var svg = d3.select("#timeline1").append("svg").attr("width", width)
      .datum(arr).call(chart);
  
  }
  timelineRect();

});


