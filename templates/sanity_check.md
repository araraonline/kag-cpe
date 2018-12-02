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
Variables:
{% for var in shp_columns %}
- `{{ var }}`
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

![City and police precincts]({{ dept.sc_figure1_path }})\

### Police precincts over census tracts

The census tracts area must cover the precincts area.

![Police precincts over census tracts]({{ dept.sc_figure2_path }})\

### Police precincts over block groups

The block groups area must cover the precincts area.

Also notice that block groups are more granular than census tracts.

![Police precincts over block groups]({{ dept.sc_figure3_path }})\

### Police precincts over block groups (zoomed in)

The areal interpolation method works best when the source polygons
(block groups) are small compared to the target polygons (police
precincts)

![Police precincts over block groups (zoomed in)]({{ dept.sc_figure4_path }})\

### Population density at various levels

The density should stay roughly the same at different levels.

The only level generated here was police precincts.

![Population density at various levels]({{ dept.sc_figure5_path }})\
