Reveal.addEventListener( 'ready', function( event ) {
	var nSlides = Reveal.getTotalSlides();

    for (i = 0; i < nSlides; i++) {
        createSlidersAnim(Reveal.getSlide(i))
    }
    
} );


function createSlidersAnim(slide) {

    if (!$(slide).attr('data-animate')) {
        return;
    }
    var slidenum = $(slide).data('animate')
    var slidenums = slidenum.split(",")
    slhtml = `<div class="slider" id="slider" style="background: #d2d2d2;width: 400px;margin: auto;margin-bottom: 15px"></div>`
    slhtml += `<img id="animimage" width="100%" style="margin:auto">`

    slide.innerHTML += slhtml
        var slider = slide.querySelector('#slider');
        noUiSlider.create(slider, {
            start: [0],
            step: 1,
            connect: true,
            range: {
                'min': parseInt(slidenums[0]),
                'max': parseInt(slidenums[1])
            }
        });
        slider.noUiSlider.on('slide', setImage);
        slider.noUiSlider.set(0)
    var animimage = slide.querySelector('#animimage')

    setImage()

    function setImage(){
        var value = 0
        value = parseInt(slider.noUiSlider.get());

        var path = $(slide).data('path')
        $("#animimage", slide).attr("src", path + "_" + value + ".png");
    }
}
