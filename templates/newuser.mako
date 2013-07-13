# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Add a new user</h1>

<form action="${request.route_url('newuser')}" class="form-inline" method="post">
  <fieldset>
    <p>New User Name: <input type="text" maxlength="100" name="newusername"></p>
    <p>New User Password: <input type="text" maxlength="100" name="newuserpass"></p>
    <p>Listname: <input type="text" maxlength="120" name="listname"></p>
    <p>Your User Name: <input type="text" maxlength="100" name="username"></p>
    <p>Your Password: <input type="text" maxlength="100" name="userpass"></p>
    <button type="submit" name="add" class="btn">Add</button>
  </fieldset>
</form>
