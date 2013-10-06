# -*- coding: utf-8 -*- 
<%inherit file="named.mako"/>

<table class="table" id="playlists">
% if following:
  % for followee in following:
  <tr><td>
    <span class="name">
    <a href="/playlist/${followee['username']}">${followee['username']}</a>
    </span>
  </td></tr>
  % endfor
% else:
  <tr><td>Nobody</td></tr>
% endif
</table>

