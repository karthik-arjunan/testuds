# jshint strict: true
((gui, $, undefined_) ->
  "use strict"

  # Public attributes
  gui.debug = on

  # Used for lookup items on some circustances
  gui.lookupUuid = null
  gui.lookup2Uuid = null  # Used for going to second level of tables. Take into account that this is used by some guis

  # "public" methods
  gui.doLog = (args...)->
    if gui.debug
      try
        console.log args

    return


  # nothing can be logged
  gui.config = gui.config or {}

  # Several convenience "constants" for tables
  gui.config.dataTablesLanguage =
    sLengthMenu: gettext("_MENU_ records per page")
    emptyTable: gettext("Empty")
    zeroRecords:  gettext("No records")
    info: gettext("Records _START_ to _END_ of _TOTAL_")
    infoEmpty: gettext("No records")
    infoFiltered: ' ' + gettext("(filtered from _MAX_ total records)")
    processing: gettext("Please wait, processing")
    search: gettext("Filter")
    thousands: django.formats.THOUSAND_SEPARATOR
    paginate:
      first: "<span class=\"fa fa-fast-backward \"></span> "
      last: "<span class=\"fa fa-fast-forward\"></span> "
      next: "<span class=\"fa fa-forward\"></span> "
      previous: "<span class=\"fa fa-backward\"></span> "
    select:
      rows:
        _: gettext("Selected %d rows")
        0: gettext("Click on a row to select it")
        1: gettext("Selected one row")


  gui.config.dataTableButtons =
    new:
      text: "<span class=\"fa fa-file\"></span> <span class=\"label-tbl-button\">" + gettext("New") + "</span>"
      css: "btn btn-action btn-tables"

    edit:
      text: "<span class=\"fa fa-edit\"></span> <span class=\"label-tbl-button\">" + gettext("Edit") + "</span>"
      css: "btn disabled btn-action btn-tables"

    delete:
      text: "<span class=\"fa fa-trash-o\"></span> <span class=\"label-tbl-button\">" + gettext("Delete") + "</span>"
      css: "btn disabled btn-alert btn-tables"

    permissions:
      text: "<span class=\"fa fa-save\"></span> <span class=\"label-tbl-button\">" + gettext("Permissions") + "</span>"
      css: "btn disabled btn-action btn-tables"

    xls:
      text: "<span class=\"fa fa-save\"></span> <span class=\"label-tbl-button\">" + gettext("Xls") + "</span>"
      css: "btn btn-export btn-tables"

    custom:
      text: null
      css: "btn btn-action btn-tables"

  gui.genRamdonId = (prefix) ->
    prefix = prefix or ""
    prefix + Math.random().toString().split(".")[1]

  gui.table = (title, table_id, options) ->
    options = options or {}
    panelId = "panel-" + table_id
    text: api.templates.evaluate("tmpl_comp_table",
      panelId: panelId
      icon: api.config.img_url + 'icons/' + (options.icon or 'maleta') + '.png'
      size: options.size or 12
      title: title
      table_id: table_id
    )
    panelId: panelId
    refreshSelector: "#" + panelId + " span.fa-refresh"

  gui.breadcrumbs = (path) ->
    items = path.split("/")
    active = items.pop()
    list = ""
    $.each items, (index, value) ->
      list += "<li><a href=\"#\">" + value + "</a></li>"
      return

    list += "<li class=\"active\">" + active + "</li>"
    "<div class=\"row\"><div class=\"col-lg-12\"><ol class=\"breadcrumb\">" + list + "</ol></div></div>"


  # By default, actionButton has class "button-accept", so you can use returned id + this class to select it
  # and do whatever is needed (for example, insert an "on click" event (this method returns id without '#'
  # Example: $('#' + id + ' .button-accept').on('click', ...
  gui.modal = (id, title, content, options) ->
    options = options or {}
    api.templates.evaluate "tmpl_comp_modal",
      id: id
      title: title
      content: content
      footer: options.footer
      button1: options.closeButton
      button2: options.actionButton

  # As previous, this creates the modal and shows it. in this case, the id of the modal returned already has '#'
  gui.launchModal = (title, content, options) ->
    options = options or {}
    id = gui.genRamdonId("modal-") # Get a random ID for this modal
    gui.appendToWorkspace gui.modal(id, title, content, options)
    id = "#" + id # for jQuery
    $(id).modal().on "hidden.bs.modal", ->
      $(id).remove()
      return

    id

  gui.notify = (message, type) ->
    gui.launchModal "<b class=\"text-" + type + "\">" + gettext("Message") + "</b>", "<span class=\"text-" + type + "\">" + message + "</span>",
      actionButton: " "
      closeButton: '<button type="button" class="btn btn-default" data-dismiss="modal">Ok</button>'

    return

  gui.failRequestModalFnc = (title) ->
    (jqXHR, textStatus, errorThrown) -> # fail on put
      # gui.doLog jqXHR, textStatus, errorThrown, jqXHR.status == 0
      errorText = if jqXHR.status == 0 then gettext('Connection failed') else jqXHR.responseText
      gui.tools.unblockUI()
      gui.launchModal "<b class=\"text-danger\">" + title + "</b>", errorText,
        actionButton: " "

      return

  gui.clearWorkspace = ->
    $("#content").empty()
    $("#minimized").empty()
    return

  gui.appendToWorkspace = (data) ->
    $(data).appendTo "#content"
    return


  # Clean up several "internal" data
  # I have discovered some "items" that are keep in memory, or that adds garbage to body (datatable && tabletools mainly)
  # Whenever we change "section", we clean up as much as we can, so we can keep things as clean as possible
  # Main problem where comming with "tabletools" and keeping references to all instances created
  gui.cleanup = ->
    gui.doLog "Cleaning up things"

    # Destroy any created datatable
    $.each $.fn.dataTable.fnTables(), (undefined_, tbl) ->
      $tbl = $(tbl).dataTable()
      $tbl.fnClearTable() # Removing data first makes things much faster
      $tbl.fnDestroy()
      return

    return

  gui.fastLink = (text, href, onClick, clas) ->
    "<span>#{text}</span><span style='float:right;'><a href='##{href}' onclick='#{onClick}(event, this);' class='#{clas}'><i class='fa fa-external-link'> </i></a></span>"

  gui.setLinksEvents = ->
    sidebarLinks = [
      {
        id: "lnk-dashboard"
        exec: gui.dashboard.link
        cleanup: true
      }
      {
        id: "lnk-service_providers"
        exec: gui.providers.link
        cleanup: true
      }
      {
        id: "lnk-authenticators"
        exec: gui.authenticators.link
        cleanup: true
      }
      {
        id: "lnk-osmanagers"
        exec: gui.osmanagers.link
        cleanup: true
      }
      {
        id: "lnk-connectivity"
        exec: gui.connectivity.link
        cleanup: true
      }
      {
        id: "lnk-deployed_services"
        exec: gui.servicesPools.link
        cleanup: true
      }
      {
        id: "lnk-clear_cache"
        exec: gui.clear_cache.link
        cleanup: false
      }
      {
        id: "lnk-configuration"
        exec: gui.configuration.link
        cleanup: false
      }
      {
        id: "lnk-gallery"
        exec: gui.gallery.link
        cleanup: true
      }
      {
        id: "lnk-reports"
        exec: gui.reports.link
        cleanup: true
      }
      {
        id: "lnk-calendars"
        exec: gui.calendars.link
        cleanup: true
      }
      {
        id: "lnk-spoolsgroup"
        exec: gui.sPoolGroups.link
        cleanup: true
      }
    ]
    $.each sidebarLinks, (index, value) ->
      gui.doLog "Adding " + value.id
      $("." + value.id).unbind("click").click (event) ->
        event.preventDefault()
        $(".navbar-toggle").trigger "click"  unless $(".navbar-toggle").css("display") is "none"
        gui.cleanup()  if value.cleanup
        $("html, body").scrollTop 0
        value.exec event
        return

      return

    return

  gui.init = ->
    gui.doLog $
    # Load jquery validator strings
    $.extend $.validator.messages,
      required: gettext("This field is required.")
      remote: gettext("Please fix this field.")
      email: gettext("Please enter a valid email address.")
      url: gettext("Please enter a valid URL.")
      date: gettext("Please enter a valid date.")
      dateISO: gettext("Please enter a valid date (ISO).")
      number: gettext("Please enter a valid number.")
      digits: gettext("Please enter only digits.")
      creditcard: gettext("Please enter a valid credit card number.")
      equalTo: gettext("Please enter the same value again.")
      maxlength: $.validator.format(gettext("Please enter no more than {0} characters."))
      minlength: $.validator.format(gettext("Please enter at least {0} characters."))
      rangelength: $.validator.format(gettext("Please enter a value between {0} and {1} characters long."))
      range: $.validator.format(gettext("Please enter a value between {0} and {1}."))
      max: $.validator.format(gettext("Please enter a value less than or equal to {0}."))
      min: $.validator.format(gettext("Please enter a value greater than or equal to {0}."))

    # Set blockui params
    $.blockUI.defaults.baseZ = 2000
    $.fn.dataTableExt.oSort["uds-date-pre"] = (s) ->
      parseInt s.split("\"")[1], 10


    # Sort for "date" columns (our "dates" are in fact postfix dates rendered as dates with locale format
    $.fn.dataTableExt.oSort["uds-date-asc"] = (x, y) ->
      val = ((if (x < y) then -1 else ((if (x > y) then 1 else 0))))
      val

    $.fn.dataTableExt.oSort["uds-date-desc"] = (x, y) ->
      val = ((if (x < y) then 1 else ((if (x > y) then -1 else 0))))
      val


    # Wait a bit before activating links to give tome tine to initializations
    setTimeout (->
      gui.setLinksEvents()
      gui.dashboard.link()
      return
    ), 500
    return

  gui.showDashboard = ->
    gui.dashboard.link()
    return
  return
) window.gui = window.gui or {}, jQuery
