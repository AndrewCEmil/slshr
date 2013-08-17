# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>${name} follows:</h1>

<ul id="playlists">
% if following:
  % for followee in following:
  <li>
    <span class="name">
    <a href="/playlist/${followee['username']}">${followee['username']}</a>
    </span>
  </li>
  % endfor
% else:
  <li>Nobody</li>
% endif
</ul>

