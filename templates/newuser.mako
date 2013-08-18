# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Add a new user</h1>

<form action="${request.route_url('newuser')}" class="form-inline" method="post">
  <fieldset>
    <p>New User Name: <input type="text" maxlength="100" name="newusername"></p>
    <p>New User Password: <input type="text" maxlength="100" name="newuserpass"></p>
    <button type="submit" name="add" class="btn">Add</button>
  </fieldset>
</form>
