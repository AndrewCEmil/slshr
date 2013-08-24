# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>${name}'s feed</h1>

<ul id="selections">
#selections format: url: string, headline: string, author: string
% if selections:
  % for selection in selections:
  <li>
    <span class="selections">
    <a href="${selection['url']}">${selection['headline']}</a> from $(selection['author'])
    </span>
  </li>
  % endfor
% else:
  <li>No Selections :(</li>
% endif
</ul>
