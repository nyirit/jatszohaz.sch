$(".datetimepicker").datepicker({
    dateFormat: 'yy-mm-dd',
    firstDay: 1
});

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    $(".slider").bootstrapSlider();

    slider_player_filter = $("#slider-player-filter");
    slider_playtime_filter = $("#slider-playtime-filter");
    game_name_filter = $('#game-name-filter');

    var refreshFilters = function(){
        player_val = slider_player_filter.val().split(',');
        min_value = parseInt(player_val[0]);
        max_value = parseInt(player_val[1]);

        length_val = slider_playtime_filter.val();
        switch (length_val) {
            case '1': length = "short"; break;
            case '2': length = "medium"; break;
            case '3': length = "long"; break;
            default: length = "all"; break;
        }

        $(".game_container")
            .filter(function() {
                var name_val = game_name_filter.val().toLowerCase();
                var playtime = !(length == "all" || $(this).attr('data-playtime-category') == length);
                var players = parseInt($(this).attr('data-min-players')) > max_value || parseInt($(this).attr('data-max-players')) < min_value;
                var name = $(this).attr('data-game-name').indexOf(name_val) == -1;
                return players || playtime || name;
            }).fadeOut(500);

        $(".game_container")
            .filter(function() {
                var name_val = game_name_filter.val().toLowerCase();
                var playtime = length == "all" || $(this).attr('data-playtime-category') == length;
                var players = !(parseInt($(this).attr('data-min-players')) > max_value || parseInt($(this).attr('data-max-players')) < min_value);
                var name = $(this).attr('data-game-name').indexOf(name_val) > -1
                return players && playtime && name;
            }).fadeIn(500);
    };
    slider_player_filter.on('change', refreshFilters);
    slider_playtime_filter.on('change', refreshFilters);
    game_name_filter.on('input', refreshFilters);
});

$(document).ready(function(){
    inventory_name_filter = $('#inventory-name-filter');

    var refreshInventoryFilters = function(){
        $(".inventory_item_container")
            .filter(function(){
                var item_name = inventory_name_filter.val().toLowerCase();
                var name = $(this).attr('data-game-name').indexOf(item_name) > -1;
                return name;
            }).fadeIn(500);

        $(".inventory_item_container")
            .filter(function(){
                var item_name = inventory_name_filter.val().toLowerCase();
                var name = $(this).attr('data-game-name').indexOf(item_name) == -1;
                return name;
            }).fadeOut(500);
    };

    inventory_name_filter.on('input', refreshInventoryFilters);
});