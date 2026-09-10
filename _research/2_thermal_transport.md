---
layout: default
title: Heat Transfer Modeling & Diagnostics
img: /assets/img/lab/rde_testbed.png
align: center
background: "#007A86"
grouping: thermal-transport
mode: dark
---

<div class="research-detail-layout">

<!-- Top section -->
<div class="research-detail-top">
  <div class="research-detail-top__figure">
    <img src="/assets/img/research/heat_flux_sensor.png" alt="Construction of the architected-wall heat flux sensor: a serpentine nickel resistance element patterned on a layered stack of silicon dioxide and Parylene HT over an aluminum body with constantan leads">
    <p class="research-detail-caption"><i>An architected-wall surface temperature sensor. The insulating layer beneath the sensing element is chosen so that the temperature swing it sees is amplified — signal gained without adding noise.</i></p>
  </div>

  <div class="research-detail-top__text">
    <p>
      You cannot design a wall you cannot predict, and you cannot validate a prediction you cannot
      measure. This thrust covers both halves: analytical methods that give surface temperature and
      heat flux in layered walls without a full conjugate simulation, and the instrumentation
      needed to check them against a real engine.
    </p>
    <p>
      The modeling side rests on a matrix formulation in the Laplace domain that yields a wall
      response function; the surface temperature is then a convolution of that function with the
      applied heat flux. It is exact, it handles arbitrarily many layers, and it is fast enough to
      sit inside a parametric study or a full vehicle drive cycle rather than a single cycle.
    </p>
    <p>Our work in this area includes:</p>
    <ul>
      <li><ins>Unsteady multilayer conduction:</ins> Analytical and semi-analytical solutions for surface temperature and heat flux in coated walls under rapidly varying thermal loads.</li>
      <li><ins>Heat flux instrumentation:</ins> Thin-film resistance sensors built on an engineered insulating layer that amplifies the measured temperature swing, patterned by lithography and by aerosol jet printing.</li>
      <li><ins>Inverse heat conduction:</ins> Recovering surface heat flux from a measured temperature, including the filtering needed to keep the inversion from amplifying noise.</li>
      <li><ins>Computational efficiency:</ins> Response-function methods that reach finite-difference accuracy orders of magnitude faster, which is what makes drive-cycle and design-space studies possible.</li>
    </ul>
  </div>
</div>

<!-- Bottom section -->
<div class="research-detail-bottom">

  <div class="research-detail-card">
    <img src="/assets/img/research/multilayer_wall.png" alt="Illustration of a one-dimensional multilayer engine wall with N layers, showing the surface heat flux boundary condition and the coolant-side temperature boundary condition">
    <h3>The Model Problem</h3>
    <p>
      An arbitrary stack of layers, a transient heat flux on one face and a coolant temperature on
      the other. Solving this exactly, and quickly, is what everything else is built on.
    </p>
  </div>

  <div class="research-detail-card">
    <img src="/assets/img/research/sensor_micrographs.jpg" alt="Micrographs of the fabricated sensing elements produced by lithographic patterning and by aerosol jet printing at two magnifications">
    <h3>Fabricated Sensors</h3>
    <p>
      Lithography gives crisp features; aerosol jet printing tolerates curved and imperfect
      surfaces. Tested in a shock tube and a motoring engine, the two agree on heat flux.
    </p>
  </div>

  <div class="research-detail-card">
    <img src="/assets/img/research/sensor_design_diagram.png" alt="Design diagram showing contours of temperature response per unit heat flux against frequency and coating thickness for Parylene HT on aluminum">
    <h3>Designing the Sensor</h3>
    <p>
      Thickness buys signal at low frequency and saturates at high frequency. The contours turn
      that trade into a thickness you can pick for a given application.
    </p>
  </div>

</div>

<div class="research-detail-refs">
  <h4>Selected work</h4>
  <ul>
    <li>J.B. Ghandhi, J.B. Carlson, R. Bonazza, D. Thompson, K. Schnittker, J.B. Andrews and G. Koutsakis, &ldquo;Rational design of an architected-wall surface temperature sensor for heat flux determination,&rdquo; <i>International Journal of Heat and Mass Transfer</i> <b>267</b>, 128982 (2026). <a href="https://doi.org/10.1016/j.ijheatmasstransfer.2026.128982">10.1016/j.ijheatmasstransfer.2026.128982</a></li>
    <li>G. Koutsakis and J.B. Ghandhi, &ldquo;Analytical solution of unsteady heat conduction in multilayer internal combustion engine walls,&rdquo; <i>Applied Thermal Engineering</i> <b>213</b>, 118681 (2022). <a href="https://doi.org/10.1016/j.applthermaleng.2022.118681">10.1016/j.applthermaleng.2022.118681</a></li>
    <li>G. Koutsakis, G.F. Nellis and J.B. Ghandhi, &ldquo;Surface temperature of a multi-layer thermal barrier coated wall subject to an unsteady heat flux,&rdquo; <i>International Journal of Heat and Mass Transfer</i> <b>155</b>, 119645 (2020). <a href="https://doi.org/10.1016/j.ijheatmasstransfer.2020.119645">10.1016/j.ijheatmasstransfer.2020.119645</a></li>
  </ul>
</div>

</div>
