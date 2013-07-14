# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>${name}'s List</h1>

<form action="${request.current_route_url()}" class="form-inline" method="post">
    <fieldset>
        <p>Headline: <input type="text" maxlength="100" name="linkname"></p>
        <p>URL: <input type="text" maxlength="1000" name="url"></p>
        <p>User Name: <input type="text" maxlength="100" name="username"></p>
        <p>Password: <input type="text" maxlength="100" name="userpass"></p>
        <button type="submit" name="add" class="btn">Add</button>
    </fieldset>
</form>

<ul id="articles">
% if articles:
  % for article in articles:
  <li>
    <span class="articles">
    <a href="${article['url']}">${article['headline']}</a>
    </span>
  </li>
  % endfor
% else:
  <li>There are no articles</li>
% endif
</ul>

