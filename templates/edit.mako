# -*- coding: utf-8 -*- 
<%inherit file="named.mako"/>

<script>
function deleteByID(id) {
    $.post('/deleteid',
    { 'targetid': id },
    function(data) {
        alert(data);
    })
}
function deleteByIdx(idx) {
    $.post('/deleteidx',
    { 'targetidx': idx },
    function(data) {
        alert(data)
    })
}
</script>

<form action="${request.current_route_url()}" class="form-inline" method="post">
    <fieldset>
        <p>Headline: <input type="text" maxlength="100" name="linkname"></p>
        <p>URL: <input type="text" maxlength="1000" name="url"></p>
        <button type="submit" name="add" class="btn">Add</button>
    </fieldset>
</form>

<table class="table" id="articles">
% if articles:
  % for article in articles:
  <tr><td>
    <a href="${article['url']}">${article['headline']}</a>
    % if "id" in article.keys():
        <button onclick="deleteByID('${article['id']}')">Delete</button>
    % else:
        <button onclick="deleteByIdx(${loop.index})">Delete</button>
    % endif
      
  </tr></td>
  % endfor
% else:
  <tr><td>There are no articles</tr></td>
% endif
</table>


