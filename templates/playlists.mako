# -*- coding: utf-8 -*- 
<%inherit file="unnamed.mako"/>

<table class="table" id="playlists">
% if playlists:
  % for playlist in playlists:
  <tr><td>
    <a href="/playlist/${playlist['_id']}">${playlist['_id']}</a>
  </td></tr>
  % endfor
% else:
  <tr><td>There are no playlists</td></td>
% endif
</table>

