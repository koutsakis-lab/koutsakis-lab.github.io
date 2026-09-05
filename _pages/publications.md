---
layout: page
permalink: /publications/
title: Publications
description: "See <a href='https://scholar.google.com/citations?user=_uw9_l0AAAAJ&hl=en'>Google Scholar</a> for the complete list."
nav: true
nav_order: 3
_styles: >
  .pub-section {
    margin-top: 2rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--global-divider-color);
    font-size: 1.35rem;
    font-weight: 600;
  }
  .pub-section:first-of-type {
    margin-top: 0;
  }
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

<h2 class="pub-section">Accepted / in press</h2>

{% bibliography -f accepted %}

<h2 class="pub-section">Published</h2>

{% bibliography %}

</div>

<script>
document.addEventListener('DOMContentLoaded',function(){
    // Script for sticky year
    document.querySelectorAll("h2.bibliography").forEach(function(e){
        e.innerHTML = '<span>'+e.innerHTML+'</span>';
    });
    // Script to add request paper button (skipped for open access papers)
    document.querySelectorAll('ol.bibliography > li > .row > div').forEach(function(e) {
      let linkBar = e.querySelectorAll('.links')[0];
      if (linkBar.querySelectorAll('.open-access-link').length > 0) return;
      let title = encodeURIComponent(e.querySelectorAll('.title')[0].textContent);
      let newLink = document.createElement('a');
      newLink.classList += 'btn btn-sm z-depth-0'
      newLink.href = 'mailto:koutsakis@unm.edu?subject=Requesting paper&body=Hi there,%0D%0AMay I request a copy of the paper "'+title+'" please?%0D%0AThank you!'
      newLink.innerHTML = 'Request paper'
      linkBar.appendChild(newLink)
    });
    // Hide a section heading ("Accepted / in press", "Published") while a
    // bibsearch filter leaves nothing visible underneath it. Runs after
    // bibsearch.js has applied its own .unloaded classes.
    let searchBox = document.getElementById('bibsearch');
    if (searchBox) {
      searchBox.addEventListener('input', function () {
        setTimeout(function () {
          document.querySelectorAll('h2.pub-section').forEach(function (heading) {
            let node = heading.nextElementSibling;
            let hasVisibleEntry = false;
            while (node && !node.classList.contains('pub-section')) {
              if (node.tagName === 'OL' && node.querySelector(':scope > li:not(.unloaded)')) {
                hasVisibleEntry = true;
                break;
              }
              node = node.nextElementSibling;
            }
            heading.classList.toggle('unloaded', !hasVisibleEntry);
          });
        }, 0);
      });
    }
});
</script>
