---
layout: page
title: Publications
slug: publications
permalink: /publications/
---

<p>Looking for a specific paper? <a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=das+rhiju" target="_blank" rel="noopener noreferrer external">Search PubMed</a>.</p>

{% assign pubs = site.publications | sort: "order" %}
{% assign years = pubs | map: "year" | uniq %}

{% for year in years %}
  <h2 class="publications-year" id="y{{ year }}">{{ year }}</h2>

  {% assign year_pubs = pubs | where: "year", year %}
  {% for pub in year_pubs %}
  <article class="publication">
    {% if pub.thumb %}
      <img class="pub-thumb" src="{{ pub.thumb | relative_url }}" alt="">
    {% else %}
      <div class="pub-thumb"></div>
    {% endif %}
    <div>
      <h3 class="pub-title">{{ pub.title }}</h3>
      <p class="pub-authors">{{ pub.authors }}</p>
      {% if pub.journal %}<p class="pub-meta"><em>{{ pub.journal }}</em></p>{% endif %}
      <p class="pub-links">
        {% if pub.pdf %}<a href="{{ pub.pdf }}" target="_blank" rel="noopener">PDF</a>{% endif %}
        {% if pub.doi %}<a href="{{ pub.doi }}" target="_blank" rel="noopener">DOI</a>{% endif %}
      </p>
    </div>
  </article>
  {% endfor %}
{% endfor %}
