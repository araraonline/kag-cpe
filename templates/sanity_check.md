---
title: 'Sanity check for department {{ name }}'
---

*this file was generated automatically by the CPE Helper package*

## Basic

- Name: {{ name }}
- Class: {{ klass }}
- Inferred city: {{ inferred_city }}
- Inferred state: {{ inferred_state }}

### Shapefile

CRS: `{{ shp_crs }}`  
Layers: `{{ shp_layers }}`  
Attributes:
{% for attr in shp_attributes %}
- `{{ attr }}`
{%- endfor %}

### Inputs

*with respect to {{ base_dir }}*

{% for file in input_files -%}
- `{{ file }}`
{% endfor %}

### Outputs

*with respect to {{ base_dir }}*

{% for file in output_files -%}
- `{{ file }}`
{% endfor %}

## Figures

### City and police precincts

The city area and precincts area must be close.

<img src="{{ dept.sc_figure1_path }}" style="max-width: 10in; max-height: 10in;" />

### Police precincts over census tracts

The census tracts area must cover the precincts area.

<img src="{{ dept.sc_figure2_path }}" style="max-width: 10in; max-height: 10in;" />

### Police precincts over block groups

The block groups area must cover the precincts area.

Also notice that block groups are more granular than census tracts.

<img src="{{ dept.sc_figure3_path }}" style="max-width: 10in; max-height: 10in;" />

### Police precincts over block groups (zoomed in)

The areal interpolation method works best when the source polygons
(block groups) are small compared to the target polygons (police
precincts)

<img src="{{ dept.sc_figure4_path }}" style="max-width: 10in; max-height: 10in;" />

### Population density at various levels

The densities should stay roughly the same at different levels.

<img src="{{ dept.sc_figure5_path }}" style="max-width: 10in; max-height: 10in;" />
