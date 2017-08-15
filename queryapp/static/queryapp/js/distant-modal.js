$(document).ready(function() {
    $.ajaxSetup({
	     beforeSend: function(xhr, settings) {
	         function getCookie(name) {
	             var cookieValue = null;
	             if (document.cookie && document.cookie != '') {
	                 var cookies = document.cookie.split(';');
	                 for (var i = 0; i < cookies.length; i++) {
	                     var cookie = jQuery.trim(cookies[i]);
	                     // Does this cookie string begin with the name we want?
	                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                         break;
	                     }
	                 }
	             }
	             return cookieValue;
	         }
	         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
	             // Only send the token to relative URLs i.e. locally.
	             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	         }
	     }
	});

    // Get the modal
    var modal = document.getElementById('reading-modal');
    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];
    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
   $(".distant-modal").on("click", function(e) {
       show_modal(e.target);
       modal.style.display = "block";
   });
});

function show_modal(target) {
    var idSplit = $(target).attr("id").split("_");
    var provenance = idSplit[0];
    var provenanceParagraph = parseInt(idSplit[1]);
    var previousOrNext = idSplit[2];
    if (previousOrNext == "previous") {
        provenanceParagraph--;
    } else if (previousOrNext == "next") {
        provenanceParagraph++;
    } else {
        console.log("Error while getting paragraph.");
        return;
    }
    var provenance =  provenance + "_" + provenanceParagraph;
    $.ajax({
        type: "POST",
        url: '/provenance/',
        data: {"provenance": provenance, "alias": $("#alias-name").html()},
        datatype: "json",
        success: function(data) {
            var modal = document.getElementById('reading-modal');
            var previous = $('<span />').attr({'class': 'distant-modal', "id": data.previous + "_previous"}).html('Previous');
            var next = $('<span />').attr({'class': 'distant-modal', "id": data.next + "_next"}).html('Next');
            $("#distant-text").empty();
            $("#distant-text").append("<h3>"+data.previous+"</h3>")
            $("#distant-text").append(previous);
            $("#distant-text").append(" ");
            $("#distant-text").append(next);
            $("#distant-text").append("<br/>");
            $("#distant-text").append("<span>"+data.content+"</span>");
            $(".distant-modal").on("click", function(e) {
                show_modal(e.target);
                modal.style.display = "block";
            });
        }
    });
}
