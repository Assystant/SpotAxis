function roundtime(minutes=0){
    var ROUNDING = minutes * 60 * 1000; /*ms*/
    start = moment();
    start = moment(Math.ceil((+start) / ROUNDING) * ROUNDING);
    start.format("D YYYY, h:mm:ss a");
    return start
}
var datetimeoptions = {
    "locale": {
        "format": 'MM/DD/YYYY h:mm A',
    },
    "drops": 'down',
    "autoUpdateInput": true,
    "alwaysShowCalendars": true,
    "startDate": roundtime(10),
    "minDate": roundtime(10),
    "opens": "center",
    "autoApply": true,
    "applyClass": "btn-info-inverse",
    "buttonClasses": "btn",
    "cancelLabel": 'Cancel',
    "singleDatePicker": true,
    "timePicker": true,
    "timePickerIncrement": 10,

}
var schedule_this = function(ev, picker){
    $card = $(this).parents('.candidate-card');
    data = {
            'candidate': $card.data('candidate'),
            'schedule': picker.element.val(),
            'offset': new Date().getTimezoneOffset(),
        }
    console.log(data)

    $content = picker.element.parents('.popover-content');
    $content.html($content.parents('.popover').prev().data('content'))
    $.ajax({
        data:data,
        url: '/ajax/schedule/',
        type: 'post',
        complete: function(){
        },
        success: function(data){
            console.log(data)
            $content.html(data.html_response);
            $content.find('.picker').on('apply.daterangepicker', schedule_this);
            $content.find('.complete-schedule').click(remove_schedule)
            predata = $content.find('.picker').attr('data-datetime')
            start = roundtime(10)
            if (predata){
                start = moment(predata,"MMMM D, YYYY, h:m")
            }
            // if (start<moment()){
            //     start = roundtime(10)

            // }
            datetimeoptions.startDate = start;
            // console.log(datetimeoptions)
            $content.find('.picker').daterangepicker(datetimeoptions);
            if(data.msg){
                alert(data.msg)
            }
            console.log($content)
            console.log($card.data('remove'))
            if($card.data('remove') == true){
                $card.click();
                console.log($content.find('.refresh-widget'))
                $('#upcoming_schedules').find('.refresh-widget').click();
            }
            else {
                $content.parents('.popover').prev().html('<span class="fa-stack fa-lg"><i class="fa fa-square-o fa-stack-2x fa-inverse"></i><i class="fa fa-lg fa-clock-o"></i></span><br>ReSchedule')
            }
        },
        error: function(er){
            console.log(er);
        }
    })
}
var remove_schedule = function(e){
    $button = $(e.target);
    $content = $button.parents('.popover-content');
    $card = $button.parents('.candidate-card');
    data = {
        'candidate': $card.data('candidate'),
    }
    $content.html($content.parents('.popover').prev().data('content'))
    $.ajax({
        data:data,
        url: '/ajax/remove-schedule/',
        type: 'post',
        complete: function(){
        },
        success: function(data){
            console.log(data)
            if(data.success == true){
                if($card.data('remove') == true){
                    $date_block = $card.parents('.date-block');
                    $card.remove();
                    if($date_block.find('.candidate-card').length == 0){
                        $date_block.remove();
                    }
                    if($('#upcoming_schedules').find('.date-block').length == 0){
                        $('#upcoming_schedules').find('.no-result').removeClass('hidden');
                    }
                }
                else {
                    $content.parents('.popover').prev().html('<span class="fa-stack fa-lg"><i class="fa fa-square-o fa-stack-2x fa-inverse"></i><i class="fa fa-lg fa-clock-o"></i></span><br> Schedule');
                    $content.parents('.popover').prev().click();
                    $('body').click();
                }
            }
            if(data.msg){
                alert(data.msg)
            }
        },
        error: function(er){
            console.log(er);
        }
    })

}
var fetch_schedule = function(){
    $this = $(this);
    $popover = $(this).data('bs.popover');
    $popover.$tip.find('.popover-content').html($popover.getContent())
    $card = $(this).parents('.candidate-card');
    data = {
            'candidate': $card.data('candidate'),
        }
        console.log($card)
    $.ajax({
        data:data,
        url: '/ajax/schedule/',
        type: 'post',
        complete: function(){
        },
        success: function(data){
            console.log(data)
            $content = $popover.$tip.find('.popover-content');
            $content.html(data.html_response);
            $content.find('.picker').on('apply.daterangepicker', schedule_this);
            $content.find('.complete-schedule').click(remove_schedule)
            predata = $content.find('.picker').attr('data-datetime')
            start = roundtime(10)
            if (predata){
                start = moment(predata,"MMMM D, YYYY, h:m")
            }
            // if (start<moment()){
            //     start = roundtime(10)

            // }
            datetimeoptions.startDate = start;
            datetimeoptions.parentEl = '#' + $content.parents('.popover')[0].id;
            // console.log(datetimeoptions)
            $content.find('.picker').daterangepicker(datetimeoptions);
            if(data.msg){
                alert(data.msg)
            }
        },
        error: function(er){
            console.log(er);
        }
    })
}
$('[data-toggle=popover]').on('shown.bs.popover',fetch_schedule)