# -*- coding: utf-8 -*-
<!DOCTYPE html>  
<html>
<head>    
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pyramid Task's List Tutorial</title>
  <meta name="author" content="Pylons Project">
  <link rel="shortcut icon" href="/static/favicon.ico">
  <link rel="stylesheet" href="/static/bootstrap.min.css">
  <link rel="stylesheet" href="/static/style.css">

</head>

<body>
  <header>
    <div class="navbar navbar-inverse">
      <div class="navbar-inner">
        <div class="container">
            <a class="brand" href="#">22 Links</a>
            <ul class="nav">
              <li class=""><a href="${request.route_url('list')}">Home</a></li>
              <li class=""><a href="${request.route_url('playlists')}">Playlists</a></li>
              <li class=""><a href="${request.route_url('new')}">New</a></li>
            </ul>
        </div>
      </div>  
  </header>    

  % if request.session.peek_flash():
  <div id="flash">
    <% flash = request.session.pop_flash() %>
    % for message in flash:
    ${message}<br>
    % endfor
  </div>
  % endif

  <div id="page" class="container">
    
    ${next.body()}

  </div>
  
</body>
</html>
