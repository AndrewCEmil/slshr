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

<div id="headerrow" class="row-fluid">
    <div class='span3'>
    </div>
    <div class='span7'>
        <h1 class="text-center">${name}'s ${listname}</h1>
    </div>
</div>

<div class="row-fluid">
    <div class='span3'>
        <ul class="table">
            <li><a href='/feed/${name}'>${name}'s feed </a></li>
            <li><a href='/followers/${name}'>${name}'s followers</a></li>
            <li><a href='/following/${name}'>${name} follows</a></li>
            % if loggedin:
                % if userfollows:
                    <button onclick="postUnfollow()">Unfallow</button>
                % else:
                    <button onclick="postfollow()">Follow</button>
                % endif
            % endif
        </ul>
    </div>

    <div class='span7'>
        ${next.body()}
    </div>
</div>
