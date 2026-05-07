---
layout: page
title: People
slug: people
hero_slug: people
permalink: /people/
---

{% assign all_current = site.people | where: "status", "current" %}
{% assign non_pi = all_current | where_exp: "p", "p.role_order != 1" | sort_natural: "last_name" %}
{% assign pi     = all_current | where: "role_order", 1 %}
{% assign current = non_pi | concat: pi %}

{% comment %}
  Alumni: order by end_year descending, then alphabetical by last_name
  within each year. Liquid's sort isn't reliably stable, so we group by
  year explicitly and concat in order.
{% endcomment %}
{% assign all_alumni = site.people | where: "status", "alumnus" %}
{% assign years = all_alumni | map: "end_year" | uniq | compact | sort | reverse %}
{% assign alumni = "" | split: "" %}
{% for y in years %}
  {% assign yr = all_alumni | where: "end_year", y | sort_natural: "last_name" %}
  {% assign alumni = alumni | concat: yr %}
{% endfor %}
{% assign no_year = all_alumni | where_exp: "a", "a.end_year == nil" | sort_natural: "last_name" %}
{% assign alumni = alumni | concat: no_year %}

<h2 class="section-heading">Current</h2>

<div class="people-grid">
{% for member in current %}
  <div class="person-card">
    {% if member.photo %}<img class="person-photo" src="{{ member.photo | relative_url }}" alt="{{ member.name }}">{% else %}<div class="person-photo"></div>{% endif %}
    <p class="person-name">{{ member.name }}</p>
    <p class="person-role">{{ member.role }}</p>
    {% if member.cv_url or member.profile_url %}
    <p class="person-links">
      {% if member.cv_url %}<a href="{{ member.cv_url }}" target="_blank" rel="noopener">Curriculum Vitae</a>{% endif %}
      {% if member.profile_url %}<a href="{{ member.profile_url }}" target="_blank" rel="noopener">Stanford profile</a>{% endif %}
    </p>
    {% endif %}
  </div>
{% endfor %}
</div>

<h2 class="section-heading">Alumni</h2>

{% assign visible = alumni | slice: 0, 30 %}
{% assign hidden  = alumni | slice: 30, 9999 %}

<ul class="alumni-list">
{% for a in visible %}
  <li>
    <span class="alum-name">{{ a.name }}</span>
    <span class="alum-role">{{ a.role }}</span>
  </li>
{% endfor %}
</ul>

{% if hidden.size > 0 %}
<details class="show-more">
  <summary>Show more alumni</summary>
  <ul class="alumni-list">
  {% for a in hidden %}
    <li>
      <span class="alum-name">{{ a.name }}</span>
      <span class="alum-role">{{ a.role }}</span>
    </li>
  {% endfor %}
  </ul>
</details>
{% endif %}
