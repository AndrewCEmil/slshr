# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>
<script>
function postfollow() {
    $.post('/follow', 
    { 'followee': "${name}" },
    function(data) {
        alert(data);
    })
}

function postUnfollow() {
    $.post('/unfollow',
    { 'unfollowee': '${name}' },
    function(data) {
        alert(data);
    })
}
</script>

<h1>${name}'s List</h1>

<p>
    <a href='/followers/${name}'>${name}'s followers</a>
    <a href='/following/${name}'>${name} follows</a>
</p>
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
<button onclick="postfollow()">Follow</button>
<button onclick="postUnfollow()">Unfallow</button>
