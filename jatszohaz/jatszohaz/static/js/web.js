$(".datetimepicker").datepicker({
    dateFormat: 'yy-mm-dd',
    firstDay: 1
});

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    $(".slider").bootstrapSlider();

    slider_player_filter = $("#slider-player-filter");
    slider_player_filter.on('change' ,function(){
        val = slider_player_filter.val().split(',');
        min_value = parseInt(val[0]);
        max_value = parseInt(val[1]);
        console.log(min_value + " " + max_value);
        $(".game_container").filter(function(){
                return parseInt($(this).attr('data-min-players')) > max_value || parseInt($(this).attr('data-max-players')) < min_value;
            }).fadeOut(500);
        $(".game_container").filter(function(){
                return !(parseInt($(this).attr('data-min-players')) > max_value || parseInt($(this).attr('data-max-players')) < min_value);
            }).fadeIn(500);
    });
});