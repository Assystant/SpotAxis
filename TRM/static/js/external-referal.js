var remove_external_referal = function(){
    $btn = $(this);
    $modal = $('#remove_external_referal-modal');
    $modal.find('#external_referal_name').html($btn.data('name'));
    $modal.find('#btn-remove-external-referal').data('id',$btn.data('id'));
    $modal.modal('show');
}
var add_external_referal = function(){
    $btn = $(this);
    vacid = $btn.data('vacancy');
    reftype = $btn.data('type');
    $textbox = $btn.parents('.form-group').find('.referal_name');
    refname = $textbox.val();
    $btn_text = $btn.html()
    $btn.html(loading_block).attr('disabled','disabled');
    $.ajax({
        url: '/ajax/add_external_referal/',
        data: {
            vid: vacid,
            reftype: reftype,
            refname: refname
        },
        type: 'post',
        complete:function(){
            $btn.html($btn_text).removeAttr('disabled');
        },
        success: function(data){
            if(data.msg){
                alert(data.msg);
            }
            if(data.success){
                console.log(data)
                if(reftype == 'ER') {
                   new_block = $(data.html).prependTo('.external_referers');
                }
                $textbox.val('');
                remove_button = new_block.find('.remove-referer');
                console.log(remove_button)
                remove_button.click(remove_external_referal);
            }
        },
        error: function(er){
            console.log(er);
        }
    })
}
$('#generate_new_external_referal').click(add_external_referal);
$('.remove-referer').click(remove_external_referal);
$('#btn-remove-external-referal').click(function(){
    refid = $(this).data('id');
    $btn = $(this);
    $modal = $('#remove_external_referal-modal');
    $btn_remove_text = $btn.html()
    $btn.html(loading_block).attr('disabled','disabled');
    $.ajax({
        url: '/ajax/remove_external_referal/',
        data: {
            refid: refid
        },
        type: 'post',
        complete:function(){
            $btn.html($btn_remove_text).removeAttr('disabled');
        },
        success: function(data){
            if(data.msg){
                alert(data.msg);
            }
            if(data.success){
                $('#list-block-'+refid).remove();
                $modal.modal('hide')
            }
        },
        error: function(er){
            console.log(er);
        }
    });
})
