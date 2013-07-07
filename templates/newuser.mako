# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Add a new user</h1>

<form action="${request.route_url('newuser')}" class="form-inline" method="post">
  <fieldset>
    <p>User Name: <input type="text" maxlength="100" name="username"></p>
    <p>Password: <input type="text" maxlength="100" name="userpass"></p>
    <p>Listname: <input type="text" maxlength="120" name="listname"></p>
    <button type="submit" name="add" class="btn">Add</button>
  </fieldset>
</form>
