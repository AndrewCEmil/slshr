# -*- coding: utf-8 -*- 
<%inherit file="named.mako"/>

<table class="table" id="playlists">
% if followers:
  % for follower in followers:
  <tr><td>
    <a href="/playlist/${follower['username']}">${follower['username']}</a>
  </td></tr>
  % endfor
% else:
  <li>There are no followers</li>
% endif
</table>

