---
layout: page
title: Publications
slug: publications
hero_slug: publications
permalink: /publications/
---

<p class="pub-search">
  <a href="https://pubmed.ncbi.nlm.nih.gov/?term=das+rhiju&sort=date" target="_blank" rel="noopener noreferrer external">
    <span class="pub-search-arrow" aria-hidden="true"></span>
    <span class="pub-search-text">Search for papers from the Das Lab on <strong>PubMed</strong></span>
  </a>
</p>

{% assign pubs = site.publications | sort: "order" %}
{% assign years = pubs | map: "year" | uniq %}

{% for year in years %}
  {% assign year_pubs = pubs | where: "year", year %}
  {% if year >= 2010 %}
  <section class="pub-year-group">
    <h2 class="pub-year" id="y{{ year }}">{{ year }}</h2>
    <div class="pub-list">
      {% for pub in year_pubs %}
      <article class="publication{% if pub.featured %} featured{% endif %}">
        {% if pub.thumb %}
          <img class="pub-thumb" src="{{ pub.thumb | relative_url }}" alt="">
        {% endif %}
        <div class="pub-text">
          <p class="pub-authors">{{ pub.authors }}</p>
          <p class="pub-title">"<span class="pub-title-text">{{ pub.title }}</span>"</p>
          {% if pub.journal %}<p class="pub-meta"><em>{{ pub.journal }}</em>{% if pub.volume %} {{ pub.volume }}{% endif %}{% if pub.pages %}, {{ pub.pages }}{% endif %}.</p>{% endif %}
          <p class="pub-links">
            {% if pub.pdf %}<a href="{{ pub.pdf }}" target="_blank" rel="noopener">Paper</a>{% endif %}
            {% if pub.doi %}<a href="{{ pub.doi }}" target="_blank" rel="noopener">Link</a>{% endif %}
            {% if pub.link_labels %}{% for label in pub.link_labels %}<a href="{{ pub.link_urls[forloop.index0] }}" target="_blank" rel="noopener">{{ label }}</a>{% endfor %}{% endif %}
          </p>
        </div>
      </article>
      {% endfor %}
    </div>
  </section>
  {% endif %}
{% endfor %}

<details class="show-more">
  <summary>Previous work by R. Das</summary>
  {% for year in years %}
    {% if year < 2010 and year > 0 %}
    {% assign year_pubs = pubs | where: "year", year %}
    <section class="pub-year-group">
      <h2 class="pub-year" id="y{{ year }}">{{ year }}</h2>
      <div class="pub-list">
        {% for pub in year_pubs %}
        <article class="publication{% if pub.featured %} featured{% endif %}">
          {% if pub.thumb %}
            <img class="pub-thumb" src="{{ pub.thumb | relative_url }}" alt="">
          {% endif %}
          <div class="pub-text">
            <p class="pub-authors">{{ pub.authors }}</p>
            <p class="pub-title">"<span class="pub-title-text">{{ pub.title }}</span>"</p>
            {% if pub.journal %}<p class="pub-meta"><em>{{ pub.journal }}</em>{% if pub.volume %} {{ pub.volume }}{% endif %}{% if pub.pages %}, {{ pub.pages }}{% endif %}.</p>{% endif %}
            <p class="pub-links">
              {% if pub.pdf %}<a href="{{ pub.pdf }}" target="_blank" rel="noopener">Paper</a>{% endif %}
              {% if pub.doi %}<a href="{{ pub.doi }}" target="_blank" rel="noopener">Link</a>{% endif %}
              {% if pub.link_labels %}{% for label in pub.link_labels %}<a href="{{ pub.link_urls[forloop.index0] }}" target="_blank" rel="noopener">{{ label }}</a>{% endfor %}{% endif %}
            </p>
          </div>
        </article>
        {% endfor %}
      </div>
    </section>
    {% endif %}
  {% endfor %}
</details>
