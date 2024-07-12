/*modal script ---*/

$(document).on('click', '[data-modal]:not(.super-modal)', function(){
	$('body').addClass('modal-open');
	selector = $(this).data('modal');
	$(selector).addClass('in');
	$(selector).find('.modal-content').addClass('in');
});
var closeModal = function(event) {
	$('.modal.in').find('.modal-content').removeClass('in');
	$('.modal.in').removeClass('in');
	$('body').removeClass('modal-open');
}

window.onclick = function(event) {
    if(event.target == $('.modal.in')[0]){
		closeModal(event);
	}
}

/*modal script end ----*/