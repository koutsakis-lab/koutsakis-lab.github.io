---
layout: page
permalink: /publications/
title: Publications
description: "See <a href='https://scholar.google.com/citations?user=_uw9_l0AAAAJ&hl=en'>Google Scholar</a> for the complete list."
nav: true
nav_order: 3
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

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
      newLink.href = 'mailto:koutsakis@unm.edu?subject=Requesting publication&body=Hello,%0D%0A%0D%0ACould you provide a copy of the paper "'+title+'" please?%0D%0A%0D%0AThank you!'
      newLink.innerHTML = 'Request paper'
      linkBar.appendChild(newLink)
    });
});
</script>
