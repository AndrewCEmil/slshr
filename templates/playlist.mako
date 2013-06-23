# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>${name}'s List</h1>

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
