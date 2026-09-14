---
title: {{ .Title | jsonify }}
date: {{ .Date.Format "2006-01-02T15:04:05-07:00" }}
{{- with .Params.tags }}
tags: {{ . | jsonify }}
{{- end }}
---

# {{ .Title }}

{{ replace .RawContent "<!--more-->" "" | safeHTML }}
