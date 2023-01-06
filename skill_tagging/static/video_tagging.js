(function($) {
  // extension method:
  $.fn.classChange = function(cb) {
    return $(this).each((_, el) => {
      new MutationObserver(mutations => {
        mutations.forEach(mutation => cb && cb(mutation.target, $(mutation.target).prop(mutation.attributeName)));
      }).observe(el, {
          attributes: true,
          attributeFilter: ['class'] // only listen for class attribute changes
        });
    });
  }

  const $foo = $("#{{ element_id }}").classChange((el, newClass) => console.log(`#${el.id} had its class updated to: ${newClass}`));

  return {};
}(window.jQuery));
