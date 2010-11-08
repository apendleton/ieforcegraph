if (typeof require != 'undefined') var underscore = require('underscore');

graphcalc = {
    distance: function(pos1, pos2) {
        return Math.sqrt(Math.pow(pos1.x - pos2.x, 2) + Math.pow(pos1.y - pos2.y, 2));
    },
    
    calculateForce: function(nodes, edges) {
        var totalForce = 0;
        _.each(nodes, function(thisNode) {
            thisNode.force = {x: 0, y: 0};
            _.each(nodes, function(otherNode) {
                if (thisNode.id != otherNode.id) {
                    if (typeof edges[thisNode.id] != 'undefined' && typeof edges[thisNode.id][otherNode.id] != 'undefined') {
                        var d = graphcalc.distance(thisNode.pos, otherNode.pos);
                        var err = edges[thisNode.id][otherNode.id] - d;
                        var factor = err / d;
                        var force = {
                            x: factor * (thisNode.pos.x - otherNode.pos.x),
                            y: factor * (thisNode.pos.y - otherNode.pos.y)
                        }
                        thisNode.force.x += force.x;
                        thisNode.force.y += force.y;
                    }
                }
            })
            totalForce += graphcalc.distance({x: 0, y: 0}, thisNode.force);
        })
        return totalForce / nodes.length;
    },
    
    applyForce: function(nodes, edges, epsilon) {
        _.each(nodes, function(node) {
            node.pos.x += epsilon * node.force.x;
            node.pos.y += epsilon * node.force.y;
        })
    },
    
    run: function(nodes, edges, epsilon, cutoff, verbose) {
        if (!epsilon) epsilon = 0.1;
        if (!cutoff) cutoff = 1;
        if (!verbose) verbose = false;
        
        while(true) {
            var force = graphcalc.calculateForce(nodes, edges);
            verbose && console.log("Average force: " + force);
            graphcalc.applyForce(nodes, edges, epsilon);
            
            var total = 0;
            _.each(nodes, function(thisNode) {
                _.each(nodes, function(otherNode) {
                    total += Math.abs(edges[thisNode.id][otherNode.id] - graphcalc.distance(thisNode.pos, otherNode.pos));
                })
            })
            verbose && console.log("Average difference: " + (total / nodes.length));
            if (force < cutoff) {
                verbose && console.log("Done");
                break;
            }
        }
    }
}

if (typeof exports != 'undefined') _.extend(exports, graphcalc);