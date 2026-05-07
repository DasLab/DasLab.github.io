---
layout: page
title: Publications
slug: publications
hero_slug: publications
permalink: /publications/
---

<p class="pub-search">
  <a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=das+rhiju" target="_blank" rel="noopener noreferrer external">
    <i class="pub-search-arrow" aria-hidden="true"></i>
    Search for papers from the Das Lab on <strong>PubMed</strong>
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
          <p class="pub-title">"{{ pub.title }}"</p>
          {% if pub.journal %}<p class="pub-meta"><em>{{ pub.journal }}</em></p>{% endif %}
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
            <p class="pub-title">"{{ pub.title }}"</p>
            {% if pub.journal %}<p class="pub-meta"><em>{{ pub.journal }}</em></p>{% endif %}
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
