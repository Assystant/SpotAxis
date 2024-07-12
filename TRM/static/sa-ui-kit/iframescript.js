
var target;

	$(document).ready(function(){
        $('a[href]').click(function(event) {
            event.preventDefault();
        }); 
		$('.editable').click(function(){
			target= $(this);
			target.attr('contentEditable', 'true');
	    	target.css('outline-color','#c9302c');
		});

		$(document).on('click', function(event){
			if($(this).get(0).activeElement.classList.contains('editable')){
				window.parent.postMessage("showPalette()" , '*');
			}
			else{
				window.parent.postMessage("hidePalette()" , '*');
			}
		});


		$('.jumbotron').append(
			'<div class="image-palette">' + 
				'<span class="fa fa-camera cameraIcon -bg-albaster -text-dark hover-light" data-modal="#image_modal"></span>' +
			'</div>'
		);

	});


$('.editable').on('focusout', function(){
	var text = $(this).text().trim();
	if($(this).text()===""){
		$(this).addClass('empty')
	}
})
.on('focusin', function(){
	$(this).removeClass('empty')
});



	/* Various function calls start here */
	var cameraIcon;
	$(document).on('click', '.cameraIcon', function(){
		cameraIcon= $(this);
	});
	
	$('#changeImage').click(function(){
		changeImage();
	});

	function changeImage(){
		var image = $('#input_image').val();
		if(image=="" || image==null)
			return;
		cameraIcon.closest('.jumbotron').attr('data-image', image);
		cameraIcon.closest('.jumbotron').css('background-image', 'url(' + image + ')');
		closeModal();
	}

	function bold(){
		document.execCommand('styleWithCSS', false, true);
		document.execCommand('bold',false,null);
		target.focus();
	}

	function italic(){
		document.execCommand('styleWithCSS', false, true);
		document.execCommand('italic',false,null);
		target.focus();
	}

	function underline(){
		document.execCommand('underline',false,null);
		target.focus();
	}

	function strikethrough(){
		document.execCommand('strikethrough',false,null);
		target.focus();
	}

	function alignLeft(){
		document.execCommand('justifyLeft',false,null);
		target.focus();
	}

	function alignRight(){
		document.execCommand('justifyRight',false,null);
		target.focus();
	}

	function alignCenter(){
		document.execCommand('justifyCenter',false,null);
		target.focus();
	}

	function alignJustify(){
		document.execCommand('justifyFull',false,null);
		target.focus();
	}

	function link(url){
		document.execCommand('createLink',false, url);
		target.focus();
	}

	function unlink(){
		document.execCommand('unlink',false,null);
		alert("Removed");
		target.focus();
	}

	function createOL(){
		document.execCommand('insertOrderedList',false,null);
		target.focus();
	}

	function createUL(){
		document.execCommand('insertUnorderedList',false,null);
		target.focus();
	}

	function fontSize(fontSize){
		document.execCommand('styleWithCSS', false, true);
		document.execCommand('fontSize',false, fontSize);
		target.focus();
	}

	function fontFamily(fontFamily){
		document.execCommand('styleWithCSS', false, true);
		document.execCommand('fontName',false, fontFamily);
		target.focus();
	}

	function colorPicker(color){
		document.execCommand('styleWithCSS', false, true);
		document.execCommand('forecolor',false,color);
		target.focus();
	}

	function erase(){
		target.find('span').removeAttr("style");
		target.focus();
	}
 
	/* Function calls end here */

/* ----------- Save functionality implemenation START--------------*/


function setLastState(blob){
	if (typeof(Storage) !== "undefined") {
    	localStorage.setItem('saved', JSON.stringify(blob));
	} 
	else {
	    console.log('Local Storage is not supported!');
	}
}

function getSavable(boolean, boolean2){
	$('.editable').blur();
	var blob = [];
	var copy = $('.takeme').clone(true);
	copy.find('.image-palette').detach();
	copy.find('.trigger_link_manager').detach();
	copy.find('.editable').removeAttr('contenteditable').removeClass('empty')
	copy.find('.job-count .badges').html('0');
	blob.push($(copy)[0].outerHTML);
	blob.push($(copy)[1].outerHTML);
	if(boolean==true){
		//calling current state of dom for diffing.
		if(boolean2 == true){
			console.log('initial')
			localStorage.setItem('saved', JSON.stringify(blob));
		}
		localStorage.setItem('fresh', JSON.stringify(blob));
	}
	else{
		//if data is being stored, save it to local storage too for last known good state
		//helps in safety check when user wants to redirect so as to not lose the unsaved work
		//called by save button with use of getSavable() without a boolean.
		setLastState(blob); //diffing purposes
		window.parent.postMessage(blob , '*'); //called for storing through ajax.
	}
}



/* ----------- Save functionality implemenation END --------------*/

var changeArea;
var clone;
$(document).on('click','.trigger_link_manager', function(){
	changeArea= $(this).parent();
	$('.link_editor').children().remove(); //remove current data from modal window
	$(this).siblings().each(function(count,object){ //iterate siblings of pencil
		if($(object).clone(true).is('i'))
			return;

		clone = $(object).clone(true);
		var handler= $(object).find('a');
		var href = handler.attr('href');
		var text= handler.text()
		$('.link_editor').append(
			'<div class="row flex-row">'+
			'<div class="field column sm-12 md-6">' + 
				'<input type="text" ' + 'value="' + text +'"' + ' class="input-field validate" required />' +
				'<label class="raise_label" for="">Title</label>' + 
			'</div>' +  
			'<div class="field column sm-12 md-6">' + 
				'<input type="text" ' + 'value="' + href +'"' + ' class="input-field validate" required />' +
				'<label class="raise_label" for="">Link</label>' + 
			'</div>'+
			'<i class="fa fa-times-circle-o -text-dark removeRow" aria-hidden="true"></i>'
			+'</div>'
		);
	});

}); //end of on click

$('.add_row').on('click', function(){
	$('.link_editor').append(
		'<div class="row flex-row">'+
			'<div class="field column sm-12 md-6">' + 
				'<input type="text" value="" class="input-field validate" required />' +
				'<label class="" for="">Title</label>' + 
			'</div>' +
			'<div class="field column sm-12 md-6">' + 
				'<input type="text" value="" class="input-field validate" required />' +
				'<label class="" for="">Link</label>' + 
			'</div>' +
			'<i class="fa fa-times-circle-o -text-dark removeRow" aria-hidden="true"></i>'
			+'</div>'
		);
})

$('.submit_links').on('click', function(){
	changeArea.children().filter('li').remove();
	
	$('.link_editor').children().filter('.row').each(function(count, object){
		var text =$(object).find('.input-field').eq(0).eq(0).val();
		var href = $(object).find('.input-field').eq(1).eq(0).val();
		temp_clone = clone.clone(true);
		temp_clone.find('a').attr('href', href);
		temp_clone.find('a').text(text);
		temp_clone.appendTo(changeArea);
	});
	closeModal();
});

$(document).on('click', '.removeRow', function(){
	$(this).parent().fadeOut(500, function(){
		if ($(this).next().prop("tagName") == 'BR') $(this).next().remove()
		$(this).remove();

	});
});


$('nav').find('ul').prepend('<span class="trigger_link_manager fa fa-pencil pop -text-dark" data-modal="#link_modal"></span>');

$('footer').find('ul').prepend('<span class="trigger_link_manager fa fa-pencil -text-dark" data-modal="#link_modal"></span>');




    /* ------ js solution to add raise effect on labels ------*/


    $(document).on('focusin', '.input-field', function() {
            $($(this).siblings()[0]).addClass('raise_label');
        })
        .on('focusout', '.input-field', function() {
            if ($(this).val().trim() === "") {
                $($(this).siblings()[0]).removeClass('raise_label');
            }
        });


	$(document).on('click', '.button', function(e){
		e.preventDefault();
		return false;
	});



/*  -------------- Prepare JSON for persistence ------------------- */

function getNavLinks(section){
	var obj = {};
	var temp={};
	var selector;
	if(section=="header") selector = 'header>nav>ul';
	else if(section=="footer") selector = 'footer>section>ul, footer>ul';

	$(selector).each(function(count, object){
		var outerCount = count;
		$(object).find('li>a').each(function(count, object){
			temp[$(object).text()] = $(object).attr('href')
			obj[outerCount] = temp;
		});
		temp ={}
	});
	return obj;
}


function getHero(){
	var temp = {};
	$('.jumbotron').each(function(count, object){
		var intermediate = {};
		/**/

		if($(object).attr('data-image')==undefined)
			background = $(object).css('background-image').replace('url(','').replace(')','');
		else
			background = $(object).attr('data-image');
			
		intermediate['background'] = background;
		intermediate['major_text'] = $(object).find('.content, .content-container>content').children().eq(0).text();
		intermediate['supporting_text'] = $(object).find('.content, .content-container>content').children().eq(1).text();
		temp[count]=intermediate;
	});
	return temp;
}

function getWhyUs(){
	var temp = {};
	if($('.box') != 0){
		$('.box>div').each(function(count, object){
			var intermediate={};
			var descrip = $(object).children().eq(1).text();
			intermediate['title'] = $(object).children().eq(0).text();
			intermediate['description'] = $(object).children().eq(1).text();
			temp[count] = intermediate;
		});
		return temp;
	}
}

function getHeroText(){
	var temp={};
	var handler = $('.header-text').find('h1, p');
	temp['major_text'] = handler.eq(0).text();
	temp['supporting_text'] = handler.eq(1).text();
	return temp;
}

function getAddresses(){
	var temp={};
	if($('footer').find('address').length!=0){
		$('footer').find('address').each(function(count, object){
			temp[count] = $(object).text();
		});

		return temp;
	}
}

function getJobHeader(){
	
	var temp = {};
	temp['paragraph'] = $('.paragraph-js-fetch').text(); 
	temp['header'] = $('.header-js-fetch').text();
	temp['tagline'] = $('.tagline-js-fetch').text();
	return temp;
}




function persistence(){
	var storage = {
		'header_links': getNavLinks('header'),
		'footer_links': getNavLinks('footer'),
		'hero_image': getHero(),
		'why_us': getWhyUs(),
		'hero_text': getHeroText(),
		'addresses': getAddresses(),
		'job_header': getJobHeader()
	}

	console.log(storage)
}

persistence();
$(document).ready(function(){
	getSavable(true, true);
});