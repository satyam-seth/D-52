$(function()
{
  $('.dropdown').on('show.bs.dropdown', function(e)
  {
      $(this).find('.dropdown-menu').first().stop(true, true).slideDown();
  });
  $('.dropdown').on('hide.bs.dropdown', function(e)
  {
      e.preventDefault();
      $(this).find('.dropdown-menu').first().stop(true, true).slideUp(400, function()
      {
          $('.dropdown').removeClass('show');
          $('.dropdown-menu').removeClass('show');
          $('.dropdown').find('.dropdown-toggle').attr('aria-expanded','false');
      });
  });
});