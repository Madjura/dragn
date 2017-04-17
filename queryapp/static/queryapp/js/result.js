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
		  ]
		});
	var options = {
			  name: 'spread',
			  animate: true, // whether to show the layout as it's running
			  ready: undefined, // Callback on layoutready
			  stop: undefined, // Callback on layoutstop
			  fit: true, // Reset viewport to fit default simulationBounds
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
		target.closedNeighborhood().nodes()
	    .selectify()
	    .select()
	    .unselectify()
	    .style({
	    	"background-color": "red"
	    })
	  ;
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
		        id: 'remove', // ID of menu item
		        title: 'remove', // Title of menu item
		        // Filters the elements to have this menu item on cxttap
		        // If the selector is not truthy no elements will have this menu item on cxttap
		        selector: 'node, edge', 
		        onClickFunction: function (event) { // The function to be executed on click
		          console.log('remove element');
		        },
		        disabled: false, // Whether the item will be created as disabled
		        show: false, // Whether the item will be shown or not
		        hasTrailingDivider: true, // Whether the item will have a trailing divider
		        coreAsWell: false // Whether core instance have this item on cxttap
		      },
		      {
		        id: 'hide',
		        title: 'hide',
		        selector: 'node, edge',
		        onClickFunction: function (event) {
		          console.log(browserTarget(event));
		        },
		        disabled: false
		      },
		      {
		        id: 'add-node',
		        title: 'add node',
		        selector: 'node',
		        coreAsWell: true,
		        onClickFunction: function (event) {
		          console.log('add node');
		        }
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