/**
 * Created with IntelliJ IDEA.
 * User: yosinobu@iij.ad.jp
 * Date: 2013/05/20
 * Time: 18:51
 * To change this template use File | Settings | File Templates.
 */

(function (global, $) {
    var _ = global._,
        USER_ID = global.tracportal.authname,
        RPC_PATH = '/login/jsonrpc',
        AVAILABLE_TICKET_QUERY = 'status!=closed&reporter=%s&or&status!=closed&owner=%s'.replace(/%s/g, USER_ID),
        DEFAULT_TICKET_FIELDS = {
            'id': {label: _('Ticket')},
            'type': {label: _('Type')},
            'time': {label: _('Created')},
            'changetime': {label: _('Updated')},
            'component': {label: _('Component')},
            'severity': {label: _('Severity')},
            'priority': {label: _('Priority')},
            'owner': {label: _('Owner')},
            'reporter': {label: _('Reporter')},
            'cc': {label: _('Cc')},
            'version': {label: _('Version')},
            'milestone': {label: _('Milestone')},
            'status': {label: _('Status')},
            'resolution': {label: _('Resolution')},
            'summary': {label: _('Summary')},
            'description': {label: _('Description')},
            'keywords': {label: _('Keywords')}
        },
        REPORTING_FIELDS = ['id', 'summary', 'milestone', 'status', 'priority', 'changetime'];

    // Models

    function Report(project) {
        this.project = project;
        this._tickets = null;
    }

    Report.prototype.getTickets = function (tids, fn) {
        var self = this,
            post_data = $.map(tids, function (tid) {
                return {method: 'ticket.get', params: [tid], id: tid};
            });
        if (tids.length === 0) {
            fn([], self.project);
            return;
        }
        jsonrpc.call(this.project.url, post_data, function (results) {
            var tickets = [];
            $.each(results, function (i, d) {
                if (d && d.result) {
                    var tid = d.result[0];
                    tickets.push(new Ticket(tid, d.result[3], self));
                }
            });
            fn(tickets, self.project);
        });
    };

    Report.prototype.getAvailableTicketIds = function (fn) {
        var post_data = {
            method: 'ticket.query',
            params: [AVAILABLE_TICKET_QUERY]
        };
        jsonrpc.call(this.project.url, post_data, function (results) {
            fn(results[0].result);
        });
    };

    Report.prototype.getAvailableTickets = function (fn) {
        var self = this;
        if (self._tickets) {
            fn(self._tickets);
            return;
        }
        this.getAvailableTicketIds(function (tids) {
            self.getTickets(tids, function (tickets) {
                self._tickets = tickets;
                fn(tickets, self.project);
            })
        });
    };

    function Ticket(tid, rpc_data, report) {
        var self = this;
        this.id = tid;
        this.report = report;
        this.url = joinPath(report.project.url, '/ticket/' + tid);
        this.fields = [];
        $.each(rpc_data, function (name, value) {
            var field = new TicketField(name, value, self);
            self.fields.push(field);
            self[name] = field;
        });
    }

    function TicketField(name, value, ticket) {
        this.name = name;
        this.ticket = ticket;
        if (value && typeof value === 'object') {
            var jc = value['__jsonclass__'];
            if (jc && jc[0] === 'datetime') {
                value = new Date(jc[1]);
            }
        }
        this.value = value;
    }

    TicketField.prototype.getLabel = function () {
        var f = DEFAULT_TICKET_FIELDS[this.name];
        return f ? f.label : this.name[0].toUpperCase() + this.name.substring(1);
    };

    TicketField.prototype.toString = function () {
        if (this.value instanceof Date) {
            return formatDate(this.value);
        }
        return this.value;
    };

    TicketField.prototype.toHTMLString = function (fn) {
        var self = this,
            post_data = {
                method: 'wiki.wikiToHtml',
                params: [self.value]
            };
        jsonrpc.call(this.ticket.report.project.url, post_data, function (results) {
            fn(results[0].result);
        });
    };

    function Roadmap(project) {
        this.project = project;
        this.max = 2;
        this.count = 0;
    }

    Roadmap.prototype.getMilestones = function (fn) {
        var self = this;
        this.getMilestoneList(function (names) {
            var post_data = $.map(names, function (name, i) {
                return {
                    id: i,
                    method: 'ticket.milestone.get',
                    params: [name]
                };
            });
            jsonrpc.call(self.project.url, post_data, function (results) {
                var milestones = [];
                $.each(results, function (i, d) {
                    if (!d.result) {
                        return;
                    }
                    var milestone = new Milestone(d.result, self);
                    if (self._filter(milestone)) {
                        milestones.push(milestone);
                    }
                });
                fn(milestones, self.project);
            });
        });
    };

    Roadmap.prototype.getMilestoneList = function (fn) {
        var post_data = {
            method: 'ticket.milestone.getAll',
            params: []
        };
        jsonrpc.call(this.project.url, post_data, function (results) {
            fn(results[0].result);
        });
    };

    Roadmap.prototype._filter = function (milestone) {
        //var range = 604800000; // 7 days : 7 * 24 * 60 * 60 * 1000
        //return !milestone.completed && milestone.due && Math.abs(milestone.due - new Date()) < range;
        if (!milestone.completed && milestone.due && (this.count < this.max)) {
            this.count++;
            return true;
        }
        return false;
    };

    function Milestone(rpc_data, roadmap) {
        var self = this;
        this.roadmap = roadmap;
        this.name = null;
        this.description = null;
        this.due = null;
        this.completed = null;
        this.status = null;
        $.each(rpc_data, function (name, value) {
            if (value && typeof value === 'object') {
                if (value['__jsonclass__'] && value['__jsonclass__'][0] === 'datetime') {
                    value = new Date(Date.parse(value['__jsonclass__'][1]));
                }
            }
            self[name] = value;
        });
    }

    Milestone.prototype.getStatus = function (fn) {
        if (this.status !== null) {
            fn(this.status);
            return;
        }
        var self = this,
            post_data = [
                {
                    id: 'total',
                    method: 'ticket.query',
                    params: [format('milestone=%s', self.name)]
                }, {
                    id: 'new',
                    method: 'ticket.query',
                    params: [format('milestone=%s&status=new', self.name)]
                }, {
                    id: 'closed',
                    method: 'ticket.query',
                    params: [format('milestone=%s&status=closed', self.name)]
                }
            ];
        jsonrpc.call(self.roadmap.project.url, post_data, function (results) {
            var status = {
                total: 0, new: 0, active: 0, closed: 0
            };
            $.each(results, function (i, d) {
                if (d && d.id && d.result) {
                    status[d.id] = d.result.length;
                }
            });
            status.active = status.total - status.closed;
            self.status = status;
            fn(status);
        });
    };

    function Timeline(project) {
        this.project = project;
    }

    Timeline.prototype.getTimeline = function (fn) {
        var self = this,
            url = joinPath(this.project.url, '/timeline?ticket=on&ticket_details=on&milestone=on&changeset=on&wiki=on&max=50&authors=&daysback=3&format=rss'),
            attr = {
                type: 'GET',
                url: fixScheme(url),
                cache: true,
                dataType: "xml",
                success: function(xml) {
                    fn(self.parseFeed(xml), self.project);
                },
                error: function (xhr) {
                    if (xhr.status === 403) {
                        var url = fixScheme(joinPath(self.project.url, '/login'));
                        $.get(url, function (data, status, xhr) {
                            if (xhr.status < 400) {
                                self.getTimeline(fn);
                            }
                        });
                    } else {
                        console.error('Failed to load the timeline.', xhr);
                    }
                }
            };
        $.ajax(attr);
    };

    Timeline.prototype.parseFeed = function (xml) {
        var self = this,
            channel = $('channel', xml).eq(0),
            feed = {};
        // RSS-2.0
        feed.items = [];
        $(channel).children().each(function () {
            var $c = $(this),
                name = $c.get(0).tagName;
            if (name !== 'item') {
                feed[name] = $c.text();
            } else {
                var item = {};
                $c.children().each(function () {
                    var $c2 = $(this),
                        name = $c2.get(0).tagName,
                        value = $c2.text();
                    if (name && value) {
                        item[name] = value;
                    }
                });
                if (self._filter(item)) {
                    feed.items.push(item);
                }
            }
        });
        return feed;
    };

    Timeline.prototype._filter = function (item) {
        return !(item && item['dc:creator'] && item['dc:creator'] === 'trac');
    };

    // utility methods

    function fixScheme(url) {
        var origin = global.location.origin || global.location.href.match(/(http:|https:)?\/\/[^/]+/)[0],
            regex = /(^(http:|https:)?\/\/)/,
            scheme = origin.match(regex)[0] || 'http://';
        if (url.match(origin)) {
            return url;
        }
        return url.replace(regex, scheme);
    }

    function joinPath(url, path) {
        var regexp = /\/$/;
        if (url.match(regexp)) {
            url = url.replace(regexp, '');
        }
        return url + path;
    }

    function format(fstring) {
        $.each(arguments, function (i, v) {
            if (i == 0) return;
            fstring = fstring.replace('%s', v);
        });
        return fstring;
    }

    var jsonrpc = {
        _pool: {},
        call: function (base_url, data, handlers) {
            var _handlers = {},
                self = this,
                pool, sid;
            if (!base_url || !data || ($.isArray(data) && data.length === 0)) {
                return;
            }
            $.extend(_handlers, {
                success: handlers.success || function () {},
                error: handlers.error || function () {},
                complete: handlers.complete || function () {}
            });
            if ($.isFunction(handlers)) {
                _handlers.success = handlers;
            }
            if (!this._pool[base_url]) {
                this._init(base_url);
            }
            pool = this._pool[base_url];
            sid = 's' + pool.length;
            pool.signatures[sid] = {
                sid: sid,
                data: data,
                handlers: _handlers
            };
            pool.length++;
            if (!pool.waiting) {
                pool.waiting = true;
                setTimeout(function () {
                    pool.waiting = false;
                    self._post(base_url);
                    self._init(base_url);
                }, 300); // pooling 300ms
            }
        },

        _init: function (base_url) {
            this._pool[base_url] = {
                signatures: {},
                waiting: false,
                length: 0
            }
        },

        _post: function (base_url) {
            var attr, signatures, is_multicall,
                params = [],
                post_data = [],
                rpc_url = fixScheme(joinPath(base_url, RPC_PATH)),
                pool = jsonrpc._pool[base_url],
            signatures = pool.signatures;
            $.each(signatures, function (sid, s) {
                var data = s.data, id = data[id] || '';

                if ($.isArray(data)) {
                    $.each(data, function (i, d) {
                        d.id =format('%s-%s.%s', sid, i, d.id || '');
                        params.push(d);
                    });
                } else {
                    data.id = format('%s-0.%s', sid, id);
                    params.push(data);
                }
            });
            post_data = { method: 'system.multicall', params: params };
            attr = {
                url: rpc_url,
                type: 'POST',
                dataType: 'json',
                data: global.JSON.stringify(post_data),
                contentType: 'application/json',
                success: function (data, status, xhr) {
                    var all_results = {};
                    if (!data || data.error) {
                        console.error('[JSON-RPC ERROR]', data, rpc_url, post_data);
                        return;
                    }
                    if (data.result) {
                        $.each(data.result, function (i, r) {
                            var sid, num, oid, matcher = r.id.match(/^(.*)-(\d+)\.(.*)$/);
                            sid = matcher[1];
                            num = matcher[2];
                            oid = matcher[3];
                            if (!all_results[sid]) {
                                all_results[sid] = [];
                            }
                            r.id = oid;
                            all_results[sid].push(r);
                        });
                        $.each(all_results, function (sid, results) {
                            signatures[sid].handlers.success(results);
                        });
                    }
                },
                error: function (ev, xhr, opts) {
                    $.each(signatures, function (sid, s) {
                        s.handlers.error(ev, xhr, opts);
                    });
                },
                complete: function (ev, xhr, opts) {
                    $.each(signatures, function (sid, s) {
                        s.handlers.complete(ev, xhr, opts);
                    });
                }
            };
            $.ajax(attr);
        }
    };

    function formatDate(d) {
        if (typeof d === 'string') {
            try {
                d = new Date(Date.parse(d));
            } catch (e) {
                console.error(e);
            }
        }
        if (!d instanceof Date) {
            return 'unknown';
        }
        var parts = {
            y: d.getFullYear(),
            m: d.getMonth() + 1,
            d: d.getDate(),
            H: d.getHours(),
            M: d.getMinutes(),
            S: d.getSeconds()
        };
        $.each(['m', 'd', 'H', 'M', 'S'], function (i, v) {
            if (parts[v] < 10) parts[v] = '0' + parts[v];
        });
        return format('%s/%s/%s %s:%s:%s', parts.y, parts.m, parts.d, parts.H, parts.M, parts.S);
    }

    // DOM operators

    function renderRoadmap(milestones, project, callback) {
        var $roadmaps = $('#roadmaps'),
            $the_roadmap = $('<div class="roadmap"/>').addClass(project.id).hide(),
            $milestones = $('<div class="milestones"/>');
        callback = callback || function () {};
        if (milestones.length < 1) {
            return;
        }
        // project name
        $the_roadmap.append($('<h3 class="project-name"/>').text(project.name));

        $.each(milestones, function (i, milestone) {
            if (!milestone.due || milestone.completed) {
                return;
            }
            var $milestone = $('<div class="milestone"/>').hide();
            $milestone.append($('<a class="ext-link" target="_blank"/>')
                    .append($('<span class="icon">&#8203;</span>'), milestone.name)
                    .attr('href', joinPath(project.url, '/milestone/' + milestone.name)))
                .append($('<span class="milestone-meta"/>')
                    .append('(', $('<span class="datetime due"/>').append(_('Due: '), formatDate(milestone.due)), ')'));
            // status
            milestone.getStatus(function (status) {
                var $status = $('<div class="status"/>'),
                    $graph = $('<div class="graph"/>'),
                    quotient_closed = status.total === 0 ? 0 : parseInt((status.closed * 100) / status.total);
                $graph.append($('<div class="closed"/>').css('width', quotient_closed + '%'));
                $status.append($graph);
                $status.append($('<div class="status-meta"/>')
                    .append($('<span class="total"/>').append(_('Total Tickets: '), status.total))
                    .append($('<span class="active"/>').append(_('Active: '), status.active)
                        .append($('<span class="new"/>').append('(', _('New: '), status.new, ')')))
                    .append($('<span class="closed"/>').append(_('Closed: '), status.closed)));
                $milestone.append($status).fadeIn('fast');
            });
            $milestones.append($milestone);
        });
        if ($milestones.find('.milestone').length > 0) {
            $roadmaps.append($the_roadmap.append($milestones));
            $the_roadmap.fadeIn(callback);
        }
    }

    function renderReport(tickets, project, callback) {
        var $reports = $('#reports'),
            $the_report = $('<div class="report"/>').addClass(project.id).hide(),
            $table = $('<table class="listing tickets"><thead><tr/></thead><tbody/></table>'),
            $header = $table.find('thead tr'),
            $body = $table.find('tbody');
        callback = callback || function () {};
        if (!tickets || tickets.length === 0) {
            callback();
            return;
        }

        // project information
        $the_report.append($('<h3 class="project-name"/>').text(project.name));

        // table header
        $.each(REPORTING_FIELDS, function (i, name) {
            var $th = $(format('<th class="%s">%s</th>', name, DEFAULT_TICKET_FIELDS[name].label));
            $header.append($th);
        });
        $header.append($(format('<th class="detail"/>')));
        $.each(tickets, function (i, ticket) {
            var $tr = $('<tr class="ticket"/>'),
                $detail = $(format('<td class="detail"><a href="javascript:void(0);">%s</a></td>', _('Detail')));
            $.each(REPORTING_FIELDS, function (i, name) {
                var value;
                if (name === 'id') {
                    value = format('<a class="ext-link" target="_blank" href="%s"><span class="icon">&#8203;</span>#%s</a>', ticket.url, ticket.id);
                } else {
                    value = ticket[name] && ticket[name].toString() || '';
                }
                $tr.append($(format('<td class="%s"><span>%s</span></td>', name, value)));
            });
            $tr.append($detail).data('ticket', ticket);
            $body.append($tr);
            $detail.click(function () {
                var ticket = $(this).parents('tr').data('ticket');
                renderTicketDetail(ticket);
            });
        });
        $reports.append($the_report.append($table));
        $the_report.fadeIn(callback);
    }

    function renderTimeline(feed, project, callback) {
        var $timelines = $('#timelines'),
            $the_timeline = $('<div class="timeline"/>').addClass(project.id).hide(),
            $items = $('<div class="items"/>');
        callback = callback || function () {};
        if (feed.items.length < 1) {
            callback();
            return;
        }

        // project information
        $the_timeline.append($('<h3 class="project-name"/>').text(project.name));
        // timeline items
        $.each(feed.items, function (i, item) {
            var $item = $('<div class="item"/>');
            $item.append($('<a class="title ext-link" target="_blank"/>')
                .append('<span class="icon">&#8203;</span>')
                .append(item.title).attr('href', item.link));
            var $descr = $('<div class="description"/>').append($(item.description).text());
            $descr.find('br').remove();
            $descr.find('a').each(function () {
                $(this).attr('target', '_blank').addClass('ext-link').prepend('<span class="icon">&#8203;</span>');
            });
            $item.append($descr).append($('<div class="timeline-meta"/>')
                .append($('<span class="datetime"/>').text(formatDate(item['pubDate'])))
                .append('(')
                .append($('<span class="creator">').append(_('Creator: ')).append(item['dc:creator'] || _('anonymous')))
                .append(')'));
            $items.append($item);
        });
        $timelines.append($the_timeline.append($items));
        $the_timeline.fadeIn(callback);
    }

    function showPopup(e) {
        var $ = $;
        if (jQuery.fn.dialog) {
            $ = jQuery;
        }
        var $popup = $('.popup');
        if (!$popup.length) {
            $popup = $('<div class="popup"/>').hide();
        }
        $popup.empty().append(e);
        $popup.dialog({
            title: _('Ticket Detail'),
            dialogClass: 'ticket-detail',
            closeText: _('Close'),
            appendTo: $('#content'),
            width: '30em',
            open: function (event, ui) {
                $popup.find('a').blur();
            }
        });
    }

    function renderTicketDetail(ticket) {
        var $ticket = $('<div class="ticket detail"/>'),
            $props = $('<table class="properties"/>'),
            $title = $('<h1 class="title"/>'),
            $descr = $('<div class="descr"/>');
        // summary
        $title.append($('<a class="ticket-id ext-link" target="_blank"/>')
                .attr('href', ticket.url)
                .append('<span class="icon">&#8203;</span>')
                .append('#' + ticket.id))
            .append($('<span class="summary"/>').append(ticket.summary.toString()));
        // properties
        $.each(ticket, function (name, field) {
            if (!(field instanceof TicketField) || $.inArray(name, ['_ts', 'summary', 'description']) !== -1) {
                return;
            }
            $props.append($('<tr/>').append(
                $('<th>/').text(field.getLabel() + ':'),
                $('<td/>').text(field.toString())
            ));
        });
        // description
        $descr.append($('<h3 class="descr-title"/>').append(ticket.description.getLabel()))
            .append($('<pre/>').text(ticket.description.toString()));
        // view html
        /*
        ticket.description.toHTMLString(function (html) {
            $descr.append(html);
        });
        */
        $ticket.append($title, $props, $descr);
        showPopup($ticket);
    }

    $.extend($.fn, {
        showLoading: function () {
            var $e = $(this);
            $e.addClass('now-loading');
            $e.css('position', 'relative');
            $e.append($('<div class="loading"/>').append($('<div class="indicator"/>'), $('<div class="loading-bg"/>')));
        },
        hideLoading: function () {
            var $e = $(this);
            $e.removeClass('now-loading');
            $e.css('position', '');
            $e.children('.loading').remove();
        }
    });

    function getProjects(context, fn) {
        if (!context) return;
        var api_path = 'dashboard/api/projects/' + context;
        $.getJSON(api_path, function (data) {
            fn(data);
        });
    }

    function Dashboard() {
        this._projects = {};
        this._ignore_projects = {};
        this.loadSettings();
    }

    Dashboard.prototype.init = function () {
        this._projects = {};
    };

    Dashboard.prototype.showReports = function () {
        var self = this,
            $e = $('#reports'),
            showNotice = function () {
                $e.append($('<span class="notice"/>').append(_('No ticket')));
            };
        $e.empty().showLoading();
        self.getProjects('report', function (projects) {
            var count = 1,
                ignore_projects = self.getIgnoreProjects('report');
            projects = $.grep(projects, function (p) {
                return $.inArray(p.id, ignore_projects) === -1;
            });
            $.each(projects, function (i, p) {
                var report = new Report(p);
                report.getAvailableTickets(function (ts, p) {
                    renderReport(ts, p, function () {
                        if ((projects.length === count) && $e.find('.report').length === 0) {
                            showNotice();
                        }
                        $e.hideLoading();
                        count++;
                        onResize();
                    });
                });
            });
            if (projects.length < 1) {
                showNotice();
                $e.hideLoading();
            }
        });
    };

    Dashboard.prototype.showRoadmaps = function () {
        var self = this,
            $e = $('#roadmaps'),
            showNotice = function () {
                $e.append($('<span class="notice"/>').append(_('No roadmap')));
            };
        $e.empty().showLoading();
        self.getProjects('roadmap', function (projects) {
            var count = 1,
                ignore_projects = self.getIgnoreProjects('roadmap');
            projects = $.grep(projects, function (p) {
                return $.inArray(p.id, ignore_projects) === -1;
            });
            $.each(projects, function (i, p) {
                var roadmap = new Roadmap(p);
                roadmap.getMilestones(function (ms, p) {
                    renderRoadmap(ms, p, function () {
                        if ((projects.length === count) && $e.find('.roadmap').length === 0) {
                            showNotice();
                        }
                        $e.hideLoading();
                        count++;
                    });
                });
            });
            if (projects.length < 1) {
                showNotice();
                $e.hideLoading();
            }
        });
    };

    Dashboard.prototype.showTimelines = function () {
        var self = this,
            $e = $('#timelines'),
            showNotice = function () {
                $e.append($('<span class="notice"/>').append(_('No recent changes')));
            };
        $e.empty().showLoading();
        self.getProjects('timeline', function (projects) {
            var count = 1,
                ignore_projects = self.getIgnoreProjects('timeline');
            projects = $.grep(projects, function (p) {
                return $.inArray(p.id, ignore_projects) === -1;
            });
            $.each(projects, function (i, p) {
                var timeline = new Timeline(p);
                timeline.getTimeline(function (feed, p) {
                    renderTimeline(feed, p, function () {
                        if ((projects.length === count) && $e.find('.timeline').size() === 0) {
                            showNotice();
                        }
                        $e.hideLoading();
                        count++;
                    });
                });
            });
            if (projects.length < 1) {
                showNotice();
                $e.hideLoading();
            }
        });
    };

    Dashboard.prototype.showSettings = function (context) {
        var self = this,
            $e = $(format('.section.%s ul.settings', context));
        if ($e.length > 0) {
            $e.toggle('fast');
            return;
        }
        getProjects(context, function (projects) {
            var $e = $('<ul class="settings"/>').hide(),
                $section = $('.section').filter('.' + context);
            $.each(projects, function (i, p) {
                var $checkbox = $('<input type="checkbox"/>').attr('value', p.id);
                if ($.inArray(p.id, self.getIgnoreProjects(context)) === -1) {
                    $checkbox.attr('checked', 'checked');
                }
                $e.append($('<li class="project"/>').append(
                    $('<label/>').append($checkbox,
                        $('<span/>').append(p.name))));
            });
            $section.append($e.show('fast'));
            $e.find('input:checkbox').change(function () {
                var pid = $(this).val();
                if ($(this).is(':checked')) {
                    $section.find(format('.%s', pid)).show();
                    self.removeIgnoreProject(context, pid);
                } else {
                    $section.find(format('.%s', pid)).hide();
                    self.addIgnoreProject(context, pid);
                }
                self.saveSettings();
            });
        });
    };

    Dashboard.prototype.getIgnoreProjects = function (context) {
        var projects = this._ignore_projects[context];
        if (projects) {
            return projects;
        }
        return [];
    };

    Dashboard.prototype.addIgnoreProject = function (context, project_id) {
        if (!this._ignore_projects[context]) {
            this._ignore_projects[context] = [];
        }
        if ($.inArray(project_id, this._ignore_projects[context]) === -1) {
            this._ignore_projects[context].push(project_id);
        }
    };

    Dashboard.prototype.removeIgnoreProject = function (context, project_id) {
        if (this._ignore_projects[context]) {
            this._ignore_projects[context] = $.grep(this._ignore_projects[context], function (n) {
                return n !== project_id;
            });
        }
    };

    Dashboard.prototype.saveSettings = function () {
        if (global.localStorage) {
            global.localStorage['ignore_projects'] = JSON.stringify(this._ignore_projects);
        }
    };

    Dashboard.prototype.loadSettings = function () {
        if (global.localStorage) {
            var data = JSON.parse(global.localStorage['ignore_projects'] || "{}");
            if (data && typeof data === 'object') {
                this._ignore_projects = data;
            }
        }
    };

    Dashboard.prototype.getProjects = function (context, fn) {
        var self = this;
        if (this._projects[context]) {
            fn(this._projects[context]);
            return;
        }
        getProjects(context, function (projects) {
            self._projects[context] = projects;
            fn(projects);
        });
    };

    // window resize handler
    function onResize() {
        var c_width = $('#content').width(),
            w_height = $(window).height(),
            l_width = 450,
            r_width = c_width - l_width - 100, // 40 is margin
            $left = $('.content.left'),
            $right = $('.content.right'),
            c_top = $left.offset().top,
            c_height = Math.ceil(w_height - c_top - 40); // 40: footer + margin

        /*
        // left section
        $left.css('width', l_width + 'px');
        $left.find('.article').css('max-height', (c_height - 50) + 'px');
        // right section
        var $articles = $right.find('.article');
        $articles.css('max-height', (c_height / $articles.length) - 80 + 'px');
        */
        // ticket summary
        if (r_width > 200) {
            $('.tickets td.summary span').css('width', Math.ceil(r_width / 2) + 'px');
        }
    }


    // document ready handler

    $(function () {
        var dashboard = new Dashboard();
        dashboard.showReports();
        dashboard.showRoadmaps();
        dashboard.showTimelines();

        $('.update').click(function () {
            var $p = $(this).parents('.section');
            if ($p.hasClass('report')) {
                dashboard.showReports();
            } else if ($p.hasClass('roadmap')) {
                dashboard.showRoadmaps();
            } else if ($p.hasClass('timeline')) {
                dashboard.showTimelines();
            }
        });
        $('.settings').click(function () {
            var $p = $(this).parents('.section');
            if ($p.hasClass('report')) {
                dashboard.showSettings('report');
            } else if ($p.hasClass('roadmap')) {
                dashboard.showSettings('roadmap');
            } else if ($p.hasClass('timeline')) {
                dashboard.showSettings('timeline');
            }
        });
        $(window).resize(onResize).resize();
    });

}(window, jQuery));