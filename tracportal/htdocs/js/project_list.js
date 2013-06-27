// -*- coding: utf-8 -*-
// filtering project list

(function() {
    var form_selector = '#search-form';
    var list_selector = '.project';
    var list_parent_selector = '.projects';
    var project_title_selector = '.info-title';
    var project_descr_selector = '.info-description';
    var indicator_selector = '#indicator';
    var timeout_id = null;

    function search(value) {
        var context = value || $(form_selector).val();
        var contexts = context.split(' ');
        var projects = $(list_selector);
        if (context === '' && contexts.length === 1) {
            projects.show('fast');
        } else {
            projects.each(function () {
                var title = $(project_title_selector, this).text() || '';
                var descr = $(project_descr_selector, this).text() || '';
                var texts = [ title, descr ].join(' ');
                var regexp, i, matched = true;
                for (i=0; i<contexts.length; i++) {
                    regexp = new RegExp(contexts[i], 'img');
                    if (!regexp.test(texts)) {
                        matched = false;
                        break;
                    }
                }
                if (matched) {
                    $(this).show('fast');
                } else {
                    $(this).hide('fast');
                }
            });
        }
    }

    $(document).ready(function () {
        $(form_selector).keyup(function () {
            $(indicator_selector).show();
            if (timeout_id) {
                window.clearTimeout(timeout_id);
            }
            timeout_id = window.setTimeout(function () {
                $(indicator_selector).hide();
                search();
            }, 500);
        });
    });
})();
