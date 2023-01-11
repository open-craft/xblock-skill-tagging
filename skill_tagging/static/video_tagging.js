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
  const $videoBlock = $("#{{block_type}}_{{ block_id }}")
  $videoBlock.classChange((el, newClass) => console.log(`#${el.id} had its class updated to: ${newClass}`));

  const $verificationDiv = $("<div>", {id: "verification-{{ block_id }}"}).html(`
{% include tag_verification_template %}
`);

  $verificationDiv.appendTo($videoBlock.find(".video-wrapper"));

  return {};
}(window.jQuery));
