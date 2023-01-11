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
  const $videoBlock = $("#{{block_type}}_{{ block_id }}");
  const $verificationDiv = $("<div>", {id: "verification-{{ block_id }}"}).html(`
{% include tag_verification_template %}
`).hide();

  $verificationDiv.appendTo($videoBlock.find(".video-player"));

  $videoBlock.classChange((_, newClass) => {
    if (newClass.includes("is-ended")) {
      $verificationDiv.show();
    } else {
      $verificationDiv.hide();
    }
  });

  return {};
}(window.jQuery));
