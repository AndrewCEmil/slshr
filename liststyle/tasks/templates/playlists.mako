# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>PlayLists</h1>

<ul id="playlists">
% if playlists:
  % for playlist in playlists:
  <li>
    <span class="name">${playlist['name']}</span>
  </li>
  % endfor
% else:
  <li>There are no playlists</li>
% endif
</ul>

