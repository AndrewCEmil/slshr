# -*- coding: utf-8 -*- 
<%inherit file="named.mako"/>

<form action="${request.current_route_url()}" class="form-inline" method="post">
    <fieldset>
        <p>Headline: <input type="text" maxlength="100" name="linkname"></p>
        <p>URL: <input type="text" maxlength="1000" name="url"></p>
        <button type="submit" name="add" class="btn">Add</button>
    </fieldset>
</form>

<table class="table" id="articles">
% if articles:
  % for article in articles:
  <tr><td>
    <a href="${article['url']}">${article['headline']}</a>
  </tr></td>
  % endfor
% else:
  <tr><td>There are no articles</tr></td>
% endif
</table>

