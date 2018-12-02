---
title: 'Sanity check for department {{ name }}'
---

*this file was generated automatically by the CPE Helper package*

## Basics

- Name: {{ name }}
- Class: {{ klass }}
- Inferred city: {{ inferred_city }}
- Inferred state: {{ inferred_state }}

## Input files

All with respect to `{{ base_dir }}`

{% for file in input_files -%}
- `{{ file }}`
{% endfor %}

## Output files

All with respect to `{{ base_dir }}`

{% for file in output_files -%}
- `{{ file }}`
{% endfor %}
