var sys = require('sys'),
    underscore = require('underscore'),
    express = require('express'),
    calc = require('./graphcalc')

var width = 500;
var height = 500;
var epsilon = 0.01;
var force_cutoff = 1;
var node_count = 50;

var Node = function(id) {
    this.id = id;
    
    this.pos = {x: Math.random() * width, y: Math.random() * height};
    this.force = {x: 0, y: 0};
    this.color = Math.random();
    this.radius = 5 + (Math.random() * 20);
}

var init = function() {
    var nodes = [];
    for (var i = 0; i < node_count; i++) {
        nodes.push(new Node(i))
    }
    
    var edges = {};
    _.each(nodes, function(thisNode) {
        if (!edges[thisNode.id]) edges[thisNode.id] = {}
        _.each(nodes, function(otherNode) {
            if (!edges[otherNode.id]) edges[otherNode.id] = {}
            if (thisNode == otherNode) {
                edges[thisNode.id][otherNode.id] = 0;
            } else if (!edges[thisNode.id][otherNode.id]) {
                var weight = (Math.abs(thisNode.color - otherNode.color) * 0.75 * width) + (2 * (thisNode.radius + otherNode.radius));
                edges[thisNode.id][otherNode.id] = weight;
                edges[otherNode.id][thisNode.id] = weight;
            }
        })
    })
    return {nodes: nodes, edges: edges};
}

var app = express.createServer();

app.get('/', function(req, res) {
    var data = init();
    graphcalc.run(data.nodes, data.edges, epsilon, force_cutoff)
    res.header('Content-Type', 'image/svg+xml');
    res.render('forcegraph.svg.ejs', {
        locals: data,
        layout: false
    })
})

app.listen(3000);