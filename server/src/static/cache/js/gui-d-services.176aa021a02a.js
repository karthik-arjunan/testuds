// Generated by CoffeeScript 1.12.7
(function() {
  gui.providers = new GuiElement(api.providers, "provi");

  gui.providers.fastLink = function(event, obj) {
    var $obj, vals;
    gui.doLog('FastLink clicked', obj);
    event.preventDefault();
    event.stopPropagation();
    $obj = $(obj);
    if ($obj.hasClass('goAuthLink')) {
      vals = $obj.attr('href').substr(1).split(',');
      gui.lookupUuid = vals[0];
      gui.lookup2Uuid = vals[1];
      return setTimeout(function() {
        return $(".lnk-authenticators").click();
      }, 50);
    } else if ($obj.hasClass('goPoolLink')) {
      gui.lookupUuid = $obj.attr('href').substr(1);
      return setTimeout(function() {
        return $(".lnk-deployed_services").click();
      }, 500);
    } else if ($obj.hasClass('goProxyGroupLink')) {
      gui.lookupUuid = $obj.attr('href').substr(1);
      return setTimeout(function() {
        return $(".lnk-proxies").click();
      }, 50);
    }
  };

  gui.providers.link = function(event) {
    "use strict";
    var clearDetails, prevTables, testButton;
    testButton = {
      testButton: {
        text: gettext("Test"),
        css: "btn-info"
      }
    };
    prevTables = [];
    clearDetails = function() {
      $.each(prevTables, function(undefined_, tbl) {
        var $tbl;
        $tbl = $(tbl).dataTable();
        $tbl.fnClearTable();
        $tbl.fnDestroy();
      });
      prevTables = [];
      $("#services-placeholder").empty();
      $("#logs-placeholder").empty();
      $("#detail-placeholder").addClass("hidden");
    };
    api.templates.get("providers", function(tmpl) {
      var tableId;
      gui.clearWorkspace();
      gui.appendToWorkspace(api.templates.evaluate(tmpl, {
        providers: "providers-placeholder",
        provider_info: "provider-info-placeholder",
        services: "services-placeholder",
        logs: "logs-placeholder"
      }));
      gui.setLinksEvents();
      $(".bottom_tabs").on("click", function(event) {
        setTimeout((function() {
          $($(event.target).attr("href") + " span.fa-refresh").click();
        }), 10);
      });
      tableId = gui.providers.table({
        icon: 'providers',
        container: "providers-placeholder",
        rowSelect: "multi",
        onCheck: function(check, items) {
          return true;
        },
        onFoundUuid: function(item) {
          setTimeout(function() {
            $('a[href="#services-placeholder_tab"]').tab('show');
            return $("#services-placeholder_tab span.fa-refresh").click();
          }, 500);
          gui.lookupUuid = gui.lookup2Uuid;
          return gui.lookup2Uuid = null;
        },
        onRefresh: function(tbl) {
          clearDetails();
        },
        onData: function(data) {
          $.each(data, function(index, value) {
            if (value.maintenance_mode === true) {
              return value.maintenance_state = gettext('In Maintenance');
            } else {
              return value.maintenance_state = gettext('Active');
            }
          });
        },
        onRowDeselect: function(deselected, dtable) {
          if (dtable.rows({
            selected: true
          }).count() !== 1) {
            clearDetails();
          }
        },
        onRowSelect: function(selected) {
          var id, logTable, services, servicesAPI, servicesTable, tmpLogTable, usage, usageAPI, usageTable;
          if (selected.length > 1) {
            clearDetails();
            return;
          }
          gui.tools.blockUI();
          clearDetails();
          $("#detail-placeholder").removeClass("hidden");
          $('#detail-placeholder a[href="#provider-info-placeholder"]').tab('show');
          gui.methods.typedShow(gui.providers, selected[0], '#provider-info-placeholder .well', gettext('Error accessing data'));
          id = selected[0].id;
          servicesAPI = api.providers.detail(id, "services", {
            permission: selected[0].permission
          });
          services = new GuiElement(servicesAPI, "services-" + selected[0].type);
          tmpLogTable = void 0;
          servicesTable = services.table({
            icon: 'services',
            container: "services-placeholder",
            doNotLoadData: true,
            rowSelect: "multi",
            onCheck: function(check, items) {
              if (check === "delete" && items.length === 1) {
                if (items[0].deployed_services_count > 0) {
                  return false;
                }
              }
              return true;
            },
            buttons: [
              "new", "edit", {
                text: gui.tools.iconAndText('fa-info', gettext('Information')),
                css: "disabled",
                disabled: true,
                click: function(vals, value, btn, tbl, refreshFnc) {
                  var val;
                  gui.doLog("Value:", value, vals[0]);
                  api.cache.clear();
                  val = vals[0];
                  return servicesAPI.invoke(val.id + "/servicesPools", function(pools) {
                    gui.doLog("Pools", pools);
                    api.templates.get("service-info", function(tmpl) {
                      var content, modalId;
                      content = api.templates.evaluate(tmpl, {
                        id: 'information',
                        pools: pools,
                        goClass: 'goLink'
                      });
                      modalId = gui.launchModal(gettext('Service information'), content, {
                        actionButton: " "
                      });
                      gui.methods.typedShow(services, val, '#information-overview', gettext('Error accessing data'));
                      tmpLogTable = services.logTable(val.id, {
                        container: "information-logs",
                        onLoad: function() {}
                      });
                      $('#information-pools-table').DataTable({
                        colReorder: true,
                        stateSave: true,
                        paging: true,
                        info: true,
                        autoWidth: false,
                        lengthChange: false,
                        pageLength: 10,
                        columnDefs: [
                          {
                            'width': '50%',
                            'targets': 0
                          }, {
                            'width': '120px',
                            'targets': 1
                          }, {
                            'width': '40px',
                            'targets': 2
                          }, {
                            'width': '160px',
                            'targets': 3
                          }
                        ],
                        ordering: true,
                        order: [[1, 'asc']],
                        dom: '<>fr<"uds-table"t>ip',
                        language: gui.config.dataTablesLanguage
                      });
                      return $('.goLink').on('click', function(event) {
                        var $this;
                        $this = $(this);
                        event.preventDefault();
                        gui.lookupUuid = $this.attr('href').substr(1);
                        $(modalId).modal('hide');
                        return setTimeout(function() {
                          return $(".lnk-deployed_services").click();
                        }, 500);
                      });
                    });
                  });
                },
                select: function(vals, value, btn, tbl, refreshFnc) {
                  if (vals.length !== 1) {
                    $(btn).addClass("disabled").prop('disabled', true);
                    return;
                  }
                  return $(btn).removeClass("disabled").prop('disabled', false);
                }
              }, "delete", "xls"
            ],
            onEdit: gui.methods.typedEdit(services, gettext("Edit service"), gettext("Service creation error")),
            onNew: gui.methods.typedNew(services, gettext("New service"), gettext("Service saving error")),
            onDelete: gui.methods.del(services, gettext("Delete service"), gettext("Service deletion error")),
            scrollToTable: false,
            onLoad: function(k) {
              gui.tools.unblockUI();
            },
            onData: function(data) {
              $.each(data, function(index, value) {
                var e;
                try {
                  if (value.proxy_id !== '-1') {
                    value.proxy = gui.fastLink(value.proxy, value.proxy_id, 'gui.providers.fastLink', 'goProxyGroupLink');
                  }
                } catch (error) {
                  e = error;
                  value.name = "<span class=\"fa fa-asterisk text-alert\"></span> " + value.name;
                }
              });
            }
          });
          logTable = gui.providers.logTable(id, {
            container: "logs-placeholder",
            doNotLoadData: true
          });
          prevTables.push(servicesTable);
          prevTables.push(logTable);
          usageAPI = api.providers.detail(id, "usage", {
            permission: selected[0].permission
          });
          usage = new GuiElement(usageAPI, "usage-" + selected[0].type);
          usageTable = usage.table({
            icon: 'usage',
            container: "usage-placeholder",
            doNotLoadData: true,
            rowSelect: "multi",
            onData: function(data) {
              return $.each(data, function(index, value) {
                value.owner = gui.fastLink(value.owner.replace(/@/, '<span class="text-danger">@</span>', value.owner_info.auth_id + ",u" + value.owner_info.user_id, 'gui.providers.fastLink', 'goAuthLink'));
                return value.pool = gui.fastLink(value.pool, value.pool_id, 'gui.providers.fastLink', 'goPoolLink');
              });
            },
            buttons: ["delete", "xls"],
            onDelete: gui.methods.del(usage, gettext("Delete user service"), gettext("User service deletion error")),
            scrollToTable: false,
            onLoad: function(k) {
              gui.tools.unblockUI();
            }
          });
          prevTables.push(usageTable);
        },
        buttons: [
          "new", "edit", {
            permission: api.permissions.MANAGEMENT,
            text: gui.tools.iconAndText('fa-ambulance', gettext("Maintenance")),
            css: "disabled",
            disabled: true,
            click: function(vals, value, btn, tbl, refreshFnc) {
              var val;
              if (vals.length > 1) {
                return;
              }
              val = vals[0];
              gui.forms.confirmModal(gettext("Maintenance Mode"), (val.maintenance_mode === false ? gettext("Enter Maintenance Mode?") : gettext("Exit Maintenance Mode?")), {
                onYes: function() {
                  gui.doLog('Val: ', val);
                  api.providers.maintenance(val.id, (function() {
                    return refreshFnc();
                  }), (function() {}));
                }
              });
              return;
            },
            select: function(vals, value, btn, tbl, refreshFnc) {
              var cls, content, val;
              if (vals.length !== 1) {
                $(btn).removeClass("btn-warning").removeClass("btn-info").addClass("disabled").prop('disabled', true);
                $(btn).empty().append(gui.tools.iconAndText('fa-ambulance', gettext("Maintenance")));
                return;
              }
              val = vals[0];
              if (val.maintenance_mode === false) {
                content = gui.tools.iconAndText('fa-ambulance', gettext('Enter maintenance Mode'));
                cls = 'btn-warning';
              } else {
                content = gui.tools.iconAndText('fa-truck', gettext('Exit Maintenance Mode'));
                cls = 'btn-info';
              }
              $(btn).removeClass("disabled").addClass(cls).prop('disabled', false);
              $(btn).empty().append(content);
            }
          }, "delete", "xls", "permissions"
        ],
        onNew: gui.methods.typedNew(gui.providers, gettext("New services provider"), gettext("Services provider creation error"), testButton),
        onEdit: gui.methods.typedEdit(gui.providers, gettext("Edit services provider"), gettext("Services Provider saving error"), testButton),
        onDelete: gui.methods.del(gui.providers, gettext("Delete services provider"), gettext("Services Provider deletion error"))
      });
    });
    return false;
  };

}).call(this);
