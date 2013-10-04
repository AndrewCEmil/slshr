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

<article id='playlistarticle'>
    <section id='playlistmain'>
        <header id='playlistheader'>
            <h1>${name}'s List</h1>
            % if loggedin:
                % if userfollows:
                    <button onclick="postfollow()">Follow</button>
                % else:
                    <button onclick="postUnfollow()">Unfallow</button>
                % endif
            % endif
        </header>

        <section id='playlistcontent'>
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
        </section>
    </section>

    <!-- sidebar section -->
    <aside id='playlistsidebar'>
        <ul>
            <li><a href='/followers/${name}'>${name}'s followers</a></li>
            <li><a href='/following/${name}'>${name} follows</a></li>
        </ul>
    </aside>
</article>
