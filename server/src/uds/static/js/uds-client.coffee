uds = @uds = @uds ? {}
$ = jQuery

uds.chrome = false
uds.safari = false
uds.ie = false
uds.firefox = false

uds.reloadCounterBase = 60
uds.counterGranurality = 2 # Every this seconds, reload time will be checked

# First, detect browser
(() ->
  ua = navigator.userAgent.toLowerCase()
  if ua.indexOf('safari') != -1
    if ua.indexOf('chrome') != -1
      uds.chrome = true
      return
    else
      uds.safari = true
      return
  if ua.indexOf('msie ') != -1 or ua.indexOf('trident/') != -1
    uds.ie = true
    return
  if ua.indexOf('firefox') != -1
    uds.firefox = true
    return
)()


blockUI = (message) ->
  message = message or "<h1><span class=\"fa fa-spinner fa-spin\"></span> " + gettext("Contacting service...") + "</h1>"
  # $.blockUI
  #  message: message
  return

unblockUI = ->
  # $.unblockUI()
  return


#Default State
isSupported = false

result = (url) ->
  unblockUI()
  if isSupported is false
    location.href = url


#Handle IE
launchIE = (el, url, alt) ->
  if $('#hiddenUdsLauncherLink').length is 0
    $('body').append('<a id="hiddenUdsLauncherLink" style="display:none;" href="#">custom protocol</a>')
  aLink = $('#hiddenUdsLauncherLink')[0]

  isSupported = false
  aLink.href = url
  #Case 1: protcolLong
  console.log 'Case 1'
  if navigator.appName == 'Microsoft Internet Explorer' and aLink.protocolLong == 'Unknown Protocol'
    isSupported = false
    result(alt)
    return
  #IE10+
  if navigator.msLaunchUri
    navigator.msLaunchUri url, (->
      unblockUI()
      isSupported = true
      return
    ), ->
      isSupported = false
      result(alt)
      return
    return
  #Case2: Open New Window, set iframe src, and access the location.href
  console.log 'Case 2'

  if $('#hiddenUdsLauncherIFrame').length is 0
    $('body').append('<iframe id="hiddenUdsLauncherIFrame" src="about:blank" style="display:none"></iframe>')
  iFrame = $('#hiddenUdsLauncherIFrame')[0]

  window.onblur = (->
    console.log 'Blur'
    window.onblur = null
    isSupported = true
    result(alt)
    return
  )

  iFrame.contentWindow.location.href = url = url

  setTimeout (->
    window.onblur = null
    result(alt)
  ), 2800

  # setTimeout (->
  #   try
  #     if myWindow.location.href is url
  #       isSupported = true
  #   catch e
  #     #Handle Exception
  #     isSupported = false
  #   if isSupported
  #     myWindow.setTimeout 'window.close()', 100
  #   else
  #     myWindow.close()
  #     result(alt)
  #   return
  # ), 100
  return

#Handle Firefox
launchMozilla = (el, url, alt) ->
  if $('#hiddenUdsLauncherIFrame').length is 0
    $('body').append('<iframe id="hiddenUdsLauncherIFrame" src="about:blank" style="display:none"></iframe>')
  iFrame = $('#hiddenUdsLauncherIFrame')[0]
  isSupported = false
  #Set iframe.src and handle exception
  console.log "Launching " + url
  try
    iFrame.contentWindow.location.href = url
    isSupported = true
    result(alt)
  catch e
    #FireFox
    if e.name == 'NS_ERROR_UNKNOWN_PROTOCOL'
      isSupported = false
      result(alt)
  return

#Handle Chrome
launchChrome = (el, url, alt) ->
  isSupported = false
  el.focus()

  window.onblur = ->
    isSupported = true
    window.onblur = null
    result(alt)
    return

  #will trigger onblur
  location.href = url
  #Note: timeout could vary as per the browser version, have a higher value
  setTimeout (->
    window.onblur = null
    if isSupported is false
      result(alt)
    return
  ), 2800
  return

# Handle safari
launchSafari = (el, url, alt) ->
  if $('#hiddenUdsLauncherIFrame').length is 0
    $('body').append('<iframe id="hiddenUdsLauncherIFrame" src="about:blank" style="display:none"></iframe>')
  iFrame = $('#hiddenUdsLauncherIFrame')[0]
  isSupported = false
  el.focus()

  window.onblur = ->
    isSupported = true
    result(alt)
    return

  iFrame.contentWindow.location.href = url

  setTimeout (->
    window.onblur = null
    result(alt)
  ), 2800


uds.launch = (el, url, alt) ->
  if url is undefined
    url = el.attr('data-href')
    url = if url? then url else el.attr('href')

  if alt is undefined
    alt = el.attr('data-href-alt')

  blockUI()

  # First get using REST the ticket for client
  url = clientRest + '/' + url.split('//')[1]
  $.ajax
    url: url
    type: "GET"
    dataType: "json"
    success: (data) ->
      if data.error? and data.error isnt ''
        unblockUI()
        alert data.error
      else
        # Fix access provided in url in case of https
        if window.location.protocol is 'https:'
          data.url = data.url.replace('uds://', 'udss://') # Ensures that protocol is https also for plugin, fixing if needed UDS provided info
        if bypassPluginDetection is false
          uds.doLaunch el, data.url, alt
        else
          window.location = data.url
      return

    error: (jqXHR, textStatus, errorThrown) ->
      unblockUI()
      alert gettext('Error accessing service: ') + textStatus
      return


  return

uds.doLaunch = (el, url, alt) ->
  if uds.firefox
    launchMozilla el, url, alt
  else if uds.chrome
    launchChrome el, url, alt
  else if uds.safari
    launchSafari el, url, alt
  else if uds.ie
    launchIE this, url, alt

  return

uds.onLink = ->
  $('.uds-service-link').on('click', ((e) ->
    e.preventDefault()

    uds.launch $(this)

    return
  ))

  return

uds.resetReloadCounter = ->
  uds.reloadCounter = uds.reloadCounterBase

uds.setReload = ->
  setTimeout uds.reload, uds.counterGranurality * 1000

uds.reload = ->
  if uds.reloadCounter == 0
    # window.location.reload()
    window.location.href = window.location.href.split('?')[0].split('#')[0] + '?tab=' + $("ul#services-tabs li.active").attr('data-name')
  else
    uds.reloadCounter -= 1
    uds.setReload()
