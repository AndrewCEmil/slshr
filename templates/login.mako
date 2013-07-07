# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Login</h1>

<form action="${request.route_url('login')}" class="form-inline" method="post">
  <fieldset>
    <p>Username: <input type="text" maxlength="100" name="username"></p>
    <p>Password: <input type="text" maxlength="100" name="password"></p>
    <button type="submit" name="add" class="btn">Add</button>
  </fieldset>
</form>
