---
layout: page
title: News
slug: news
hero_slug: news
permalink: /news/
---

{% comment %}
  Show every post from the most recent year up top; everything older tucks
  under "Previous news". Early in a year that could be a very short list, so
  always show at least 10 posts.
{% endcomment %}
{% assign posts = site.news | sort: "date" | reverse %}
{% assign latest_year = posts[0].date | date: "%Y" %}
{% assign count = 0 %}
{% for post in posts %}
  {% assign year = post.date | date: "%Y" %}
  {% if year != latest_year %}{% break %}{% endif %}
  {% assign count = count | plus: 1 %}
{% endfor %}
{% if count < 10 %}{% assign count = 10 %}{% endif %}
{% assign recent = posts | slice: 0, count %}
{% assign older  = posts | slice: count, 1000 %}

<ul class="news-list">
{% for post in recent %}
  <li class="news-entry">
    {% if post.image %}
      <img class="news-thumb" src="{{ post.image | relative_url }}" alt="">
    {% else %}
      <div class="news-thumb"></div>
    {% endif %}
    <div class="news-body">
      <p class="news-date">{{ post.date | date: "%B %-d, %Y" }}</p>
      {{ post.content }}
    </div>
  </li>
{% endfor %}
</ul>

{% if older.size > 0 %}
<details class="show-more">
  <summary>Previous news</summary>
  <ul class="news-list">
    {% for post in older %}
    <li class="news-entry">
      {% if post.image %}
        <img class="news-thumb" src="{{ post.image | relative_url }}" alt="">
      {% else %}
        <div class="news-thumb"></div>
      {% endif %}
      <div class="news-body">
        <p class="news-date">{{ post.date | date: "%B %-d, %Y" }}</p>
        {{ post.content }}
      </div>
    </li>
    {% endfor %}
  </ul>
</details>
{% endif %}
