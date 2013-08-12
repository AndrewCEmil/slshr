# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>PlayLists</h1>

<ul id="playlists">
% if followers:
  % for follower in followers:
  <li>
    <span class="name">
    <a href="/playlist/${follower['username']}">${follower['username']}</a>
    </span>
  </li>
  % endfor
% else:
  <li>There are no followers</li>
% endif
</ul>

