$(window).on('load', function() {

  /*Page Loader active
  ========================================================*/
  $('#preloader').fadeOut();

  // Sticky Nav
    $(window).on('scroll', function() {
        if ($(window).scrollTop() > 50) {
            $('.scrolling-navbar').addClass('top-nav-collapse');
        } else {
            $('.scrolling-navbar').removeClass('top-nav-collapse');
        }
    });

    // one page navigation
    $('.navbar-nav').onePageNav({
      currentClass: 'active'
    });

    /* Auto Close Responsive Navbar on Click
    ========================================================*/
    function close_toggle() {
        if ($(window).width() <= 768) {
            $('.navbar-collapse a').on('click', function () {
                $('.navbar-collapse').collapse('hide');
            });
        }
        else {
            $('.navbar .navbar-inverse a').off('click');
        }
    }
    close_toggle();
    $(window).resize(close_toggle);

    /* WOW Scroll Spy
    ========================================================*/
     var wow = new WOW({
      //disabled for mobile
        mobile: false
    });

    wow.init();

     /* Testimonials Carousel
    ========================================================*/
    var owl = $("#testimonials");
      owl.owlCarousel({
        loop: true,
        nav: false,
        dots: true,
        center: true,
        margin: 15,
        slideSpeed: 1000,
        stopOnHover: true,
        autoPlay: true,
        responsiveClass: true,
        responsiveRefreshRate: true,
        responsive : {
            0 : {
                items: 1
            },
            768 : {
                items: 2
            },
            960 : {
                items: 3
            },
            1200 : {
                items: 3
            },
            1920 : {
                items: 3
            }
        }
      });


    /* Back Top Link active
    ========================================================*/
      var offset = 200;
      var duration = 500;
      $(window).scroll(function() {
        if ($(this).scrollTop() > offset) {
          $('.back-to-top').fadeIn(400);
        } else {
          $('.back-to-top').fadeOut(400);
        }
      });

      $('.back-to-top').on('click',function(event) {
        event.preventDefault();
        $('html, body').animate({
          scrollTop: 0
        }, 600);
        return false;
      });

  });


jQuery( "#tabs-profile" ).on( "tabsactivate", function( event, ui ) {
    jQuery( '.flexslider .slide' ).resize();
});

function calendar() {
    $('.component-datepicker.default').datepicker({
        autoclose: true,
        startDate: "today",
    });

    $('.component-datepicker.today').datepicker({
        autoclose: true,
        startDate: "today",
        todayHighlight: true
    });

    $('.component-datepicker.past-enabled').datepicker({
        autoclose: true,
    });

    $('.component-datepicker.format').datepicker({
        autoclose: true,
        format: "dd-mm-yyyy",
    });

    $('.component-datepicker.autoclose').datepicker();

    $('.component-datepicker.disabled-week').datepicker({
        autoclose: true,
        daysOfWeekDisabled: "0"
    });

    $('.component-datepicker.highlighted-week').datepicker({
        autoclose: true,
        daysOfWeekHighlighted: "0"
    });

    $('.component-datepicker.mnth').datepicker({
        autoclose: true,
        minViewMode: 1,
        format: "mm/yy"
    });

    $('.component-datepicker.multidate').datepicker({
        multidate: true,
        multidateSeparator: " , "
    });

    $('.component-datepicker.input-daterange').datepicker({
        autoclose: true
    });

    $('.component-datepicker.inline-calendar').datepicker();

    $('.datetimepicker').datetimepicker({
        showClose: true
    });
}

$(function(){
    $('.cpf').mask('000.000.000-00', {reverse: true});
});

