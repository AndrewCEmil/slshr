# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<div id="headerrow" class="row-fluid">
    <div class='span3'>
    </div>
    <div class='span7'>
        <h1 class="text-center">${listname}</h1>
    </div>
</div>

<div class="row-fluid">
    <div class='span3'>
    </div>

    <div class='span7'>
        ${next.body()}
    </div>
</div>
