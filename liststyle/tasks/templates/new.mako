# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Add a new task</h1>

<form action="${request.route_url('new')}" class="form-inline" method="post">
  <fieldset>
    <input type="text" maxlength="100" name="name">
    <button type="submit" name="add" class="btn">Add</button>
  </fieldset>
</form>
