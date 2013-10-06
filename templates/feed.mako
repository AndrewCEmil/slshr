# -*- coding: utf-8 -*- 
<%inherit file="named.mako"/>

<table class="table" id="selections">
% if selections:
  % for selection in selections:
  <tr><td>
    <a href="${selection['url']}">${selection['headline']}</a> from ${selection['author']}
  </td></tr>
  % endfor
% else:
  <tr><td>No Selections :(</td></tr>
% endif
</table>
