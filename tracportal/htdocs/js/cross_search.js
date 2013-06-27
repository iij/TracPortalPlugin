// -*- coding: utf-8 -*-

(function (global, $) {
    var API_PATH = '/login/jsonrpc';

    function SearchResult(rpc_data) {
        this.link = rpc_data[0];
        this.summary = rpc_data[1];
        this.datetime = null;
        this.author = rpc_data[3];
        this.description = rpc_data[4];
        if (typeof rpc_data[2] === 'object') {
            var jsonclass = rpc_data[2]['__jsonclass__'];
            if (jsonclass[0] === 'datetime') {
                this.datetime = new Date(Date.parse(jsonclass[1]));
            }
        }
    }

    function search(url, query, filters, fn) {
        var post_data = {
            params: [query, filters],
            method: 'search.performSearch'
        },
            attr = {
                url: url,
                type: 'POST',
                dataType: 'json',
                data: global.JSON.stringify(post_data),
                contentType: 'application/json',
                success: fn
            };
        $.ajax(attr);
    }

    function getFilters(all) {
        var filters = [];
        var selector = '.filter';
        if (!all) {
            selector += ':checked';
        }
        $(selector).each(function () {
            filters.push($(this).attr('name'));
        });
        return filters;
    }

    function filterResults(results) {
        var ignore_default = $('#ignore_trac_default').is(':checked'),
            max = $('#num').val(),
            n = 0;
        return $.grep(results, function (r) {
            return (!ignore_default || r.author !== 'trac') && (max > n++);
        });
    }

    function renderResults(results, project, query, filters) {
        var max = $('#num').val(),
            slim_results = $('#slim_results').is(':checked'),
            $title = $('<h3 class="project_search_title"/>'),
            url_query,
            $wrap,
            $dl;
        url_query = (function (q) {
            q = '?q=' + query;
            $.each(filters, function (i, v) {
                q += '&' + v + '=on';
            });
            return q;
        }(query));
        if (!$.isArray(results) || (slim_results && results.length === 0)) {
            return;
        }
        $wrap = $('<div></div>')
            .append($title.append($('<a class="project_page ext-link" target="_blank"></a>')
                .attr('href', project.href).append($('<span class="icon">&#8203;</span>'), project.name)));
        $dl = $('<dl class="results"></dl>');
        $.each(results, function (i, r) {
            var $dt = $('<dt/>').append($('<a target="_blank" class="ext-link"><span class="icon">&#8203;</span></a>')
                    .attr('href', r.link).append(r.summary)),
                $dd1 = $('<dd class="searchable"/>').text(r.description),
                $dd2 = $('<dd/>')
                    .append($('<span class="author"/>').text(_('Author') + ': ' + r.author))
                    .append($('<span class="date"/>').html(formatDate(r.datetime)));
            $dl.append($dt).append($dd1).append($dd2);
            return true;
        });
        if (results.length >= max) {
            $dl.append($('<dt/>')
                .append($('<a class="search_page" target="_blank"/>')
                    .attr('href', project.href + "/search" + url_query).text(_('More Search Results ...'))));
        }
        if (results.length === 0) {
            $dl.append($('<span class="notfound"></span>').text(_('No matches found.')));
        }
        $('#search_results').append($wrap.append($dl));
        // event handler for fold/expand results
        $title.click(function (e) {
            if (e.target.nodeName !== 'A') {
                $('.results', $(this).parent()).toggle();
            }
        });
        highlight(query);
    }

    function highlight(query) {
        var $e = $('.searchable'),
            terms = [];
        $.each(query.split(/(".*?"|'.*?'|\s+)/), function () {
            if (terms.length < 10) {
                var term = this.replace(/^\s+$/, '')
                        .replace(/^['"]/, '')
                        .replace(/['"]$/, '');
                if (term.length >= 3)
                    terms.push(term);
            }
        });
        $.each(terms, function (idx) {
            $e.highlightText(this.toLowerCase(), 'searchword' + (idx % 5));
        });
    }

    function crossSearch() {
        var q = $("#q").val(),
            all_projects = !!($('#all_projects:checked').length),
            filters = getFilters(),
            finished = 0,
            $search_status = $('#search_status'),
            $projects,
            results_num = 0;
        if (!q) return;
        $('#search_results').empty();
        $search_status.empty();
        $projects = all_projects ? $('.project') : $('.project:checked');
        $projects.each(function () {
            var self = this,
                url = fixScheme($(this).val() + API_PATH);
            search(url, q, filters, function (data) {
                var results = [];
                if (data && data.result && (data.result.length > 0)) {
                    results = filterResults($.map(data.result, function (r) {
                        return new SearchResult(r);
                    }));
                    results_num += results.length;
                    renderResults(results, {
                        name: $(self).attr('data-name'),
                        env_name: $(self).attr('data-env_name'),
                        href: $(self).val()
                    }, q, filters);
                }
                finished++;
                if ($projects.length <= finished) {
                    $search_status.append($('<span/>').text(_('%s results').replace('%s', results_num)));
                }
            });
        });
        $("#search_title").show();
    }

    function fixScheme(url) {
        var origin = global.location.origin || global.location.href.match(/(http:|https:)?\/\/[^/]+/)[0],
            regex = /(^(http:|https:)?\/\/)/,
            scheme = origin.match(regex)[0] || 'http://';
        if (url.match(origin)) {
            return url;
        }
        return url.replace(regex, scheme);
    }

    function formatDate(d) {
        if (typeof d === 'string') {
            try {
                d = new Date(Date.parse(d));
            } catch (e) {
                console.log(e);
            }
        }
        if (!d instanceof Date) {
            return 'unknown';
        }
        return [[d.getFullYear(), d.getMonth()+1, d.getDay()].join('/'),
            [d.getHours(), d.getMinutes(), d.getSeconds()].join(':')].join(' ');
    }

    $(document).ready(function () {
        $('#indicator').hide().ajaxStart(function () {
            $(this).show();
        }).ajaxStop(function () {
            $(this).hide();
        });
        $('#search_title').hide();
        $('#cross_search').submit(function () {
            crossSearch();
            return false;
        });
        $('.project').change(function () {
            var checked = $(this).is(':checked');
            if (checked) {
                $('#all_projects').removeAttr('checked');
            }
        });
        if ($('#q').focus().val()) {
            crossSearch();
        }
    });
}(window, jQuery));
