# -*- coding: utf-8 -*- 
<%inherit file="named.mako"/>

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
