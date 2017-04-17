function browserTarget(e) {
	var target = e.cyTarget;
	if (!target) {
		target = e.target;
	}
	return target;
}

$( document ).ready(function() {
	var cy = cytoscape({
		  container: $("#cy"),
		  boxSelectionEnabled: true,
		  style: [
		    {
		      selector: 'node',
		      style: {
		        "content": "data(id)",
		        "text-halign": "center",
		        "text-valign": "center",
		        "width": "data(size)",
		        "height": "data(size)",
		      }
		    },
		    {
		    	selector: "edge",
		    	style: {
		    		"line-color": "data(color)"
		    	}
		    },
		    {
		    	selector: ".hidden",
		    	style: {
		    		"visibility": "hidden"
		    	}
		    }
		  ]
		});
	var options = {
			  name: 'spread',
			  animate: true, // whether to show the layout as it's running
			  ready: undefined, // Callback on layoutready
			  stop: undefined, // Callback on layoutstop
			  fit: false, // Reset viewport to fit default simulationBounds
			  minDist: 100, // Minimum distance between nodes
			  padding: 20, // Padding
			  expandingFactor: -1.0, // If the network does not satisfy the minDist
			  // criterium then it expands the network of this amount
			  // If it is set to -1.0 the amount of expansion is automatically
			  // calculated based on the minDist, the aspect ratio and the
			  // number of nodes
			  maxFruchtermanReingoldIterations: 50, // Maximum number of initial force-directed iterations
			  maxExpandIterations: 4, // Maximum number of expanding iterations
			  boundingBox: undefined, // Constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
			  randomize: false // uses random initial node positions on true
	};
	cy.add(graphElements);
	var layout = cy.elements().layout(options);
	try {
		layout.run();
	} catch (err) {}

	cy.nodes().on("tap", function(e) {
		// this check is needed for cross browser compability
		var target = browserTarget(e);
		
		var connectedNodes = target.closedNeighborhood().nodes();
		connectedNodes
	    .selectify()
	    .select()
	    .unselectify()
	    .style({
	    	"background-color": "red"
	    });
		var options = {
				  name: 'concentric',

				  fit: true, // whether to fit the viewport to the graph
				  padding: 30, // the padding on fit
				  startAngle: 3 / 2 * Math.PI, // where nodes start in radians
				  sweep: undefined, // how many radians should be between the first and last node (defaults to full circle)
				  clockwise: true, // whether the layout should go clockwise (true) or counterclockwise/anticlockwise (false)
				  equidistant: false, // whether levels have an equal radial distance betwen them, may cause bounding box overflow
				  minNodeSpacing: 10, // min spacing between outside of nodes (used for radius adjustment)
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  avoidOverlap: true, // prevents node overlap, may overflow boundingBox if not enough space
				  height: undefined, // height of layout area (overrides container height)
				  width: undefined, // width of layout area (overrides container width)
				  concentric: function( node ){ // returns numeric value for each node, placing higher nodes in levels towards the centre
				  return node.degree();
				  },
				  levelWidth: function( nodes ){ // the variation of concentric values in each level
				  return nodes.maxDegree() / 4;
				  },
				  animate: false, // whether to transition the node positions
				  animationDuration: 500, // duration of animation in ms if enabled
				  animationEasing: undefined, // easing of animation if enabled
				  ready: undefined, // callback on layoutready
				  stop: undefined // callback on layoutstop
				};
		var layout = connectedNodes.union(connectedNodes.connectedEdges()).layout(options);
		try {
			console.log("LAYOUT");
			layout.run();
		} catch (err) {}
	});
	
	cy.on("tap", function(e) {
		var target = browserTarget(e);
		if (target == cy) {
			cy.nodes()
				.selectify()
				.unselect()
				.unselectify()
				.style({
					"background-color": "grey"
				});
			;
		}
	});
	
	var menu = {
		    // List of initial menu items
		    menuItems: [
		      {
		        id: 'hide-this',
		        title: 'Hide this and all connected',
		        selector: 'node',
		        onClickFunction: function (event) {
		        	// get the selected node
		        	var target = browserTarget(event);
		        	
		        	// get all edges connected to this node
		        	var edges = target.connectedEdges();
		        	
		        	var connectedNodes = edges.connectedNodes();

		    		target.addClass("hidden");
		    		edges.addClass("hidden");
		        	edges.connectedNodes().forEach(function(node) {
		        		if (node.connectedEdges().filter(":visible").size() == 0) {
		        			node.addClass("hidden");
		        		}
		        	});
		        	
		        },
		        coreAsWell: false,
		        disabled: false
		      },
		      {
		    	id: "show-only",
		    	title: "Show only this and directly connected",
		    	selector: "node",
		    	onClickFunction: function(event) {
		    		var target = browserTarget(event);
		    		var edges = target.connectedEdges();
		    		var connectedNodes = edges.connectedNodes();
		    		cy.collection()
		    		.union(target)
		    		.union(edges)
		    		.union(connectedNodes)
		    		.absoluteComplement()
		    		.addClass("hidden");
		    	},
		        coreAsWell: false,
		      },
		      {
		    	  id: "show-all",
		    	  title: "Show all nodes and edges",
		    	  selector: "node, edge",
			      coreAsWell: true,
		    	  onClickFunction: function(event) {
			    		cy.nodes().filter(":hidden").removeClass("hidden");
			    		cy.edges().filter(":hidden").removeClass("hidden");
		    	  },
		    	  disabled: false
		      }
		    ],
		    // css classes that menu items will have
		    menuItemClasses: [
		      // add class names to this list
		    ],
		    // css classes that context menu will have
		    contextMenuClasses: [
		      // add class names to this list
		    ]
		};
	cy.contextMenus(menu);
});