$('.covervid-video').coverVid(1920, 1080);
fullscreen();
$(window).resize(fullscreen);

function fullscreen() {
    var masthead = $('.covervid-wrapper');
    console.log(masthead);
    var windowH = $(window).height();
    var windowW = $(window).width();

    masthead.width(windowW);
    masthead.height(windowH);
}
