function showDashBoard(){
      for(var i = 1; i <= 3; i++) {
        $('.col'+i).each(function(){
            $(this).addClass('fadeInForward-'+i).removeClass('fadeOutback');
        });
      }
    }

    function fadeDashBoard(){
      for(var i = 1; i <= 3; i++) {
        $('.col'+i).addClass('fadeOutback').removeClass('fadeInForward-'+i);
      }
    }
    
   // fadeDashBoard();

    heightNormal = $('.mosaic-wrapper').height();
   
    $(".lock-thumb").click(function(){
        fadeDashBoard();
        $('.login-screen').addClass('slidePageInFromLeft').removeClass('slidePageBackLeft');
    });
    
    $('#unlock-button').click(function(){
          $('.login-screen').removeClass('slidePageInFromLeft').addClass('slidePageBackLeft');
          showDashBoard();
    });

  $('.big, .small').each(function(){
    var $this= $(this),
        page = $this.data('page');
    $this.on('click',function(){
      $('.page.'+page).addClass('openpage');
      var currentHeight = $('.page.'+page+' .row').height() +25;
      $('.page.'+page).height(currentHeight);

      $('.mosaic-wrapper').height(currentHeight);

      fadeDashBoard();
    })
  });

  $('.close-button').click(function(){
    $(this).parent().addClass('slidePageLeft')
          .one('webkitAnimationEnd oanimationend msAnimationEnd animationend', function(e) {
                $(this).removeClass('slidePageLeft').removeClass('openpage');
              });

      $('.mosaic-wrapper').height(heightNormal);

      showDashBoard();
  });
  