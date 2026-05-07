---
layout: page
title: News
slug: news
permalink: /news/
---

{% assign posts = site.news | sort: "date" | reverse %}
{% assign recent = posts | slice: 0, 20 %}
{% assign older  = posts | slice: 20, 1000 %}

<ul class="news-list">
{% for post in recent %}
  <li class="news-entry">
    {% if post.image %}
      <img class="news-thumb" src="{{ post.image | relative_url }}" alt="">
    {% else %}
      <div class="news-thumb"></div>
    {% endif %}
    <div>
      <p class="news-date">{{ post.date | date: "%B %-d, %Y" }}</p>
      <h2 class="news-headline"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
      <p class="news-excerpt">{{ post.content | strip_html | truncate: 220 }}</p>
    </div>
  </li>
{% endfor %}
</ul>

{% if older.size > 0 %}
<details class="show-more">
  <summary>Previous news from the Das Lab ({{ older.size }})</summary>
  <ul class="news-list">
    {% for post in older %}
    <li class="news-entry">
      {% if post.image %}
        <img class="news-thumb" src="{{ post.image | relative_url }}" alt="">
      {% else %}
        <div class="news-thumb"></div>
      {% endif %}
      <div>
        <p class="news-date">{{ post.date | date: "%B %-d, %Y" }}</p>
        <h2 class="news-headline"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
        <p class="news-excerpt">{{ post.content | strip_html | truncate: 220 }}</p>
      </div>
    </li>
    {% endfor %}
  </ul>
</details>
{% endif %}
