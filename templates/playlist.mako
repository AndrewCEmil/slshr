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

<h1 class="text-center">${name}'s List</h1>

<div class="container-fluid">
    <div class="row-fluid">
        <div class='span3'>
            <ul class="table">
                <li><a href='/followers/${name}'>${name}'s followers</a></li>
                <li><a href='/following/${name}'>${name} follows</a></li>
                % if loggedin:
                    % if userfollows:
                        <button onclick="postfollow()">Follow</button>
                    % else:
                        <button onclick="postUnfollow()">Unfallow</button>
                    % endif
                % endif
            </ul>
        </div>
        
        <div class='span7'>
            <table class="table" id="articles">
            % if articles:
              % for article in articles:
              <tr><td>
                <a href="${article['url']}">${article['headline']}</a>
              </tr></td>
              % endfor
            % else:
              <tr><td>There are no articles</tr></td>
            % endif
            </table>
        </div>
    </div>
</div>
