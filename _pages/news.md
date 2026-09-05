---
layout: page
title: News
permalink: /news/
nav: true
nav_order: 5
_styles: >
  .news-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .news-list__item {
    display: flex;
    gap: 1.5rem;
    align-items: baseline;
    padding: 1.1rem 0;
    border-bottom: 1px solid var(--global-divider-color);
  }
  .news-list__item:first-child {
    padding-top: 0;
  }
  .news-list__date {
    flex: 0 0 auto;
    width: 9rem;
    color: var(--global-text-color-light);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }
  .news-list__body {
    flex: 1 1 auto;
    min-width: 0;
  }
  .news-list__body p {
    margin: 0;
  }
  @media (max-width: 576px) {
    .news-list__item {
      flex-direction: column;
      gap: 0.35rem;
    }
    .news-list__date {
      width: auto;
    }
  }
---

<ul class="news-list">
{% assign news = site.news | sort: 'date' | reverse %}
{% for item in news %}
  <li class="news-list__item">
    <time class="news-list__date">{{ item.date | date: '%B %-d, %Y' }}</time>
    <div class="news-list__body">{{ item.content }}</div>
  </li>
{% endfor %}
</ul>
