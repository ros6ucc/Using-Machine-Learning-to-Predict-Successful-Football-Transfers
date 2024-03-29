console.log("Script loaded");
$(document).ready(function() {
    $("#player").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: suggestPlayerURL + request.term,
                dataType: "json",
                success: function(data) {
                    response($.map(data, function(item) {
                        return {
                            label: item.name, // This is displayed in the suggestions.
                            value: item.name, // This is the value inserted into the input field.
                            image: item.image_url // This can be used for an image tag.
                        };
                    }));
                }
            });
        },
        minLength: 2, // Trigger the autocomplete with at least two characters.
        select: function(event, ui) {
            // This event is triggered when a selection is made.
        }
    }).autocomplete('instance')._renderItem = function(ul, item) {
        // Custom rendering of each suggestion item.
        return $("<li>")
            .append("<div><img src='" + item.image + "' style='width: 80px; height: auto; margin-right: 10px;'><span>" + item.label + "</span></div>")
            .appendTo(ul);
    };
    
                                  
    // Club suggestions
    $("#club").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "/suggest_club/" + request.term,
                dataType: "json",
                success: function(data) {
                    response(data.suggestions);
                }
            });
        },
        minLength: 2
    });

});