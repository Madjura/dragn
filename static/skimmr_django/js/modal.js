$(document).ready(function () {

    var modal = document.getElementById('myModal');

// Get the button that opens the modal
    var btn = $("#help");
// Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    btn.click(function () {
        modal.style.display = "block";
        var container = $("#modal-content");
        scrollTo = $("#" + btn.attr("section"));

        container.scrollTop(
            scrollTo.offset().top - container.offset().top + container.scrollTop()
        );
    });
// When the user clicks on <span> (x), close the modal
    span.onclick = function () {
        modal.style.display = "none";
    }

    $("#myModal").click(function (event) {
        if (event.target.id == "myModal") {
            $("#myModal").fadeOut(400, function () {
                $("#myModal").hide();
            });
        }
    });

});