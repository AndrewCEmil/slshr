# -*- coding: utf-8 -*- 
<%inherit file="named.mako"/>

<script>
function deleteByID(id, idx) {
    $.post('/deleteid',
    { 'targetid': id },
    function(data) {
        alert(data);
    })
    $('#article' + idx).remove() 
}
function deleteByIdx(idx) {
    $.post('/deleteidx',
    { 'targetidx': idx },
    function(data) {
        alert(data)
    })
    $('#article' + idx).remove() 
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
  <tr id='article${loop.index}'><td>
    <a href="${article['url']}">${article['headline']}</a>
    % if "id" in article.keys():
        <button onclick="deleteByID('${article['id']}', ${loop.index})">Delete</button>
    % else:
        <button onclick="deleteByIdx(${loop.index})">Delete</button>
    % endif
      
  </td></tr>
  % endfor
% else:
  <tr><td>There are no articles</tr></td>
% endif
</table>


