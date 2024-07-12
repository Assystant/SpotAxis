function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
$(document).ready(function() {


    // initial hiding of left palette
    $('.palette-container').hide();

    window.onbeforeunload = function (e) {
        sendMessage('getSavable(true)');
        var savedState = localStorage.getItem('saved');
        var freshState = localStorage.getItem('fresh');
        if(savedState!=freshState)
            return "Do you really want to close?";
    };


    //send Message to iframe whenever there's a click on left palette 
    //or message pass

    function sendMessage(command) {
        document.getElementById('doc-iframe').contentWindow.postMessage(command, '*');
    }


    // listen to message from iframe to parent
    window.addEventListener('message', function(e) {

        if( Object.prototype.toString.call(e.data) === '[object Array]' ) {
            data = {
                    'above_jobs' : e.data[0],
                    'below_jobs' : e.data[1],
                    'csrf_token': getCookie('csrftoken')
                }
            console.log(data)
            $.ajax({
                data : data,
                url: '/ajax/save_template/',
                type: 'post',
                success: function(data){
                    if(data.success){
                        $('#savepage').blur().html('<i class="fa fa-check-square-o fa-fw"></i> Saved').addClass('saved');
                        setTimeout(function(){
                            $('#savepage').removeClass('saved').html('Save')
                        }, 1800);
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
        else{
            var run = '<script>' + e.data + "<\/script>";
            $('body').append(run);    
        }
        
    });


    /* Save page */
    $(document).on('click', '#savepage',  function(){
        sendMessage('getSavable()');
    });




    /* --- left palette code starts here ---*/




    //--- sub section from here  --- palette options which further have their own menus

    $('.list').focus(function() {
        $('.palette-list').css({
            'visibility': 'visible',
            'opacity': '1'
        });
    });

    $('.list').focusout(function() {
        $('.palette-list').css({
            'visibility': 'hidden',
            'opacity': '0'
        });
    });

    $('.align').focus(function() {
        $('.palette-align').css({
            'visibility': 'visible',
            'opacity': '1'
        });
    });
    $('.align').focusout(function() {
        $('.palette-align').css({
            'visibility': 'hidden',
            'opacity': '0'
        });
    });

    $('#font-size').focus(function() {
        $('.palette-fontsize').css({
            'visibility': 'visible',
            'opacity': '1'
        });
    });

    $('#font-family').focus(function() {
        $('.palette-fontfamily').css({
            'visibility': 'visible',
            'opacity': '1'
        });
    });

    $('#font-family').focusout(function() {
        $('.palette-fontfamily').css({
            'visibility': 'hidden',
            'opacity': '0'
        });
    });


    $('#font-size').focusout(function() {
        $('.palette-fontsize').css({
            'visibility': 'hidden',
            'opacity': '0'
        });
    });

    // --- sub section ends here  ---




    //--- sub section from here  --- palette buttons send message to iframe

    $('#color').click(function() {
        $('#picker').trigger("click");
    });


    $('#picker').on('change', function() {
        var color = $('#picker').val();
        sendMessage('colorPicker("' + color + '")');
    });

    $('#italic').click(function() {
        sendMessage('italic()');
    });

    $('#bold').click(function() {
        sendMessage('bold()');
    });

    $('#underline').click(function() {
        sendMessage('underline()');
    });

    $('#strikethrough').click(function() {
        sendMessage('strikethrough()');
    });

    $('#align-left').click(function() {
        sendMessage('alignLeft()');
    });

    $('#align-right').click(function() {
        sendMessage('alignRight()');
    });

    $('#align-justify').click(function() {
        sendMessage('alignJustify()');
    });

    $('#align-center').click(function() {
        sendMessage('alignCenter()');
    });

    $('#link_button').click(function(){
        $('#input_url').val("http://")
    });

    $('#link').click(function() {
        var link = $('#input_url').val();
        sendMessage('link("' + link + '")');
        $('#input_url').val("");
        closeModal();
    });

    $('#unlink').click(function() {
        sendMessage('unlink()');
    });

    $('#ordered-list').click(function() {
        sendMessage('createOL()');
    });


    $('#unordered-list').click(function() {
        sendMessage('createUL()');
    });

    $('.font-button').click(function() {
        var fontFamily = $(this).val();
        document.execCommand('styleWithCSS', false, true);
        document.execCommand('fontName', false, fontFamily);
    });

    $('.fontFamily-button').click(function() {
        var fontFamily = $(this).val();
        sendMessage('fontFamily("' + fontFamily + '")');
    });

    $('.fontSize-button').click(function() {
        var fontSize = $(this).val();
        sendMessage('fontSize(' + fontSize + ')');
    });

    $('#eraser').click(function() {
        sendMessage('erase()');
    });


    /*Image palette code here*/

    $('#changeImage').click(function() {
        sendMessage('changeImage()');
    });


    // --- sub section ends here --- 


    /* --- left palette code ends here ---*/




    /* ------ js solution to add raise effect on labels ------*/


    $(document).on('focusin', '.input-field', function() {
            $($(this).siblings()[0]).addClass('raise_label');
        })
        .on('focusout', '.input-field', function() {
            if ($(this).val().trim() === "") {
                $($(this).siblings()[0]).removeClass('raise_label');
            }
        });

    $('.back_to_template').click(function(e){
        e.preventDefault();
        sendMessage('getSavable(true)');
        $this = $(this)
        setTimeout(function(){
            location.href = $this.attr('href')
        },300);

    })
});
