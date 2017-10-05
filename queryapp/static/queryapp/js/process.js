$(document).ready(function () {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
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
    $("#process-formt").submit(function(event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: provUrl,
            data: {"provenance": provenance, "alias": $("#alias-name").html(), "matches": matches},
            datatype: "json",
            success: function(data) {
                var modal = document.getElementById('reading-modal');
                var matches = data.matches;
                console.log("AJAX MATCHES: " + matches);
                var previous = $('<span />').attr({'class': 'distant-modal', "id": data.previous + "_previous"}).html('Previous');
                var next = $('<span />').attr({'class': 'distant-modal', "id": data.next + "_next"}).html('Next');
                $("#distant-text").empty();
                $("#modal-matches").html(matches);
                $("#distant-text").append("<h3>"+data.previous+"</h3>");
                $("#distant-text").append(previous);
                $("#distant-text").append(" ");
                $("#distant-text").append(next);
                $("#distant-text").append("<br/>");
                $("#distant-text").append("<span id='modal-result-text'>"+data.content+"</span>");
                $(".distant-modal").on("click", function(e) {
                    show_modal(e.target);
                    modal.style.display = "block";
                });
            }
        });
    });
});
