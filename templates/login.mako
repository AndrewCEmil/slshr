# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Login</h1>

<p><a href='${request.route_url('newuser')'>Register</a></p>

<form action="${request.route_url('login')}" class="form-inline" method="post">
  <fieldset>
    <input name="_csrf" type="hidden" value="${request.session.get_csrf_token()}">
    <p>Username: <input type="text" maxlength="100" name="username"></p>
    <p>Password: <input type="password" maxlength="100" name="password"></p>
    <button type="submit" name="add" class="btn">Add</button>
  </fieldset>
</form>
