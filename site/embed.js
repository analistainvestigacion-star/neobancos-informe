/*
 * Informe vivo de Neobancos y Billeteras Digitales (Colombia Fintech).
 * Uso en WordPress (bloque "HTML personalizado"):
 *   <div id="cf-neobancos"></div>
 *   <script src="https://analistainvestigacion-star.github.io/neobancos-informe/embed.js" defer></script>
 * Lee data/informe.json del mismo lugar donde vive este script.
 */
(function () {
  "use strict";
  var script = document.currentScript;
  var BASE = script ? script.src.replace(/[^/]*$/, "") : "./";
  var CDN = {
    echarts: "https://cdnjs.cloudflare.com/ajax/libs/echarts/5.5.0/echarts.min.js",
    marked: "https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js",
  };
  var COLOR = {
    navy: "#2B3241", mint: "#ADD5C2", sage: "#9DC4AC", olive: "#888D71", teal: "#ABDDDC",
    terracotta: "#D79475", lavender: "#B5A1C2", apricot: "#F4A873", chartreuse: "#DFE4AB",
    grey: "#DBD6D7", linea: "#E1E3DD", cuerpo: "#4A505D", suave: "#6B707B", papel: "#F6F7F4",
  };
  // Navy domina; los acentos entran solo cuando hay varias series.
  var PALETA = [COLOR.navy, COLOR.sage, COLOR.terracotta, COLOR.olive, COLOR.lavender, COLOR.apricot,
    COLOR.teal, "#5C6B8A", "#8FB7A2", "#B07A5E", "#7E7396", "#C4C99A"];
  var MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

  function cargar(src) {
    return new Promise(function (ok, mal) {
      var s = document.createElement("script");
      s.src = src; s.onload = ok; s.onerror = mal; document.head.appendChild(s);
    });
  }

  // ------------------------------------------------------------------ datos
  var D = null;
  var NOMBRES = {};

  function serie(ind, ent) {
    return (D.series[ind] && D.series[ind][ent]) || [];
  }
  function resolverFecha(ind, corte) {
    if (!corte || corte === "informe") return D.meta.corte_informe;
    if (corte === "base") return D.meta.corte_base;
    if (corte === "ultimo") return D.ultimo[ind];
    if (/^\d{4}-\d{2}$/.test(corte)) {
      var d = new Date(+corte.slice(0, 4), +corte.slice(5, 7), 0);
      return d.toISOString().slice(0, 10);
    }
    return corte;
  }
  // Valor en una fecha; para series trimestrales usa el último dato <= fecha (máx. 3 meses atrás).
  function valor(ind, ent, corte) {
    var f = resolverFecha(ind, corte), s = serie(ind, ent), mejor = null;
    for (var i = 0; i < s.length; i++) {
      if (s[i][0] === f) return s[i][1];
      if (s[i][0] < f && mesesEntre(s[i][0], f) <= 3) mejor = s[i][1];
    }
    return mejor;
  }
  function mesesEntre(a, b) {
    return (+b.slice(0, 4) - +a.slice(0, 4)) * 12 + (+b.slice(5, 7) - +a.slice(5, 7));
  }
  // Suma de un flujo en el año; solo si están los 12 meses (si no, "n.d." en vez de una cifra incompleta).
  function anual(ind, ent, anio) {
    var s = serie(ind, ent), t = 0, n = 0;
    for (var i = 0; i < s.length; i++) if (s[i][0].slice(0, 4) === String(anio)) { t += s[i][1]; n++; }
    return n === 12 ? t : null;
  }
  function anioInforme() { return +D.meta.corte_informe.slice(0, 4); }

  // ------------------------------------------------------------- formatos
  var nf = function (d) { return new Intl.NumberFormat("es-CO", { maximumFractionDigits: d, minimumFractionDigits: d }); };
  function fmt(v, f) {
    if (v === null || v === undefined || isNaN(v)) return "n.d.";
    switch (f) {
      case "billones": return (v < 0 ? "-$" : "$") + nf(1).format(Math.abs(v) / 1e12) + " billones";
      case "milm": return (v < 0 ? "-$" : "$") + nf(0).format(Math.abs(v) / 1e9) + " mil millones";
      case "dec": return nf(1).format(v);
      case "millones": return nf(1).format(v / 1e6) + " millones";
      case "miles": return nf(0).format(v / 1e3) + " mil";
      case "pct": return nf(1).format(v * 100) + " %";
      case "tasa": return nf(1).format(v) + " % E.A.";
      case "pp": return nf(1).format(v * 100) + " p. p.";
      default: return nf(0).format(v);
    }
  }
  function fmtFecha(f) {
    if (!f) return "n.d.";
    return MESES[+f.slice(5, 7) - 1] + "-" + f.slice(0, 4);
  }
  function eje(f) {
    return {
      billones: function (v) { return nf(1).format(v / 1e12); },
      milm: function (v) { return nf(0).format(v / 1e9); },
      millones: function (v) { return nf(1).format(v / 1e6); },
      miles: function (v) { return nf(0).format(v / 1e3); },
      pct: function (v) { return nf(0).format(v * 100) + "%"; },
      tasa: function (v) { return nf(1).format(v) + "%"; },
    }[f] || function (v) { return nf(0).format(v); };
  }
  var UNIDAD = { billones: "billones de pesos", milm: "miles de millones de pesos", millones: "millones",
    miles: "miles", pct: "%", tasa: "% efectivo anual" };

  // ---------------------------------------------------------- marcadores
  // {{v:ind:ent:corte:fmt}}  {{crec:ind:ent}}  {{anual:ind:ent:anio:fmt}}  {{crec_anual:ind:ent}}
  // {{part:ind:ent:comp:corte}}  {{ratio:num:den:ent:corte}}  {{verbo:ind:ent}}  {{fecha:ind}}
  // {{nombre:ent}}  {{corte}}  {{base}}
  function crec(ind, ent) {
    var a = valor(ind, ent, "informe"), b = valor(ind, ent, "base");
    return a !== null && b ? a / b - 1 : null;
  }
  function crecAnual(ind, ent) {
    var y = anioInforme(), a = anual(ind, ent, y), b = anual(ind, ent, y - 1);
    return a !== null && b ? a / b - 1 : null;
  }
  function marcador(expr) {
    var p = expr.trim().split(":"), op = p[0];
    try {
      switch (op) {
        case "v": return fmt(valor(p[1], p[2], p[3]), p[4]);
        case "crec": return fmt(crec(p[1], p[2]), "pct");
        case "crec_anual": return fmt(crecAnual(p[1], p[2]), "pct");
        case "anual": return fmt(anual(p[1], p[2], p[3] === "informe" || !p[3] ? anioInforme() : p[3]), p[4]);
        case "part": {
          var a = valor(p[1], p[2], p[4]), b = valor(p[1], p[3], p[4]);
          return fmt(a !== null && b ? a / b : null, "pct");
        }
        case "ratio": {
          var n = valor(p[1], p[3], p[4]), d = valor(p[2], p[3], p[4]);
          return fmt(n !== null && d ? n / d : null, p[5] || "pct");
        }
        case "verbo": {
          var c = p[0] === "verbo" && p[3] === "anual" ? crecAnual(p[1], p[2]) : crec(p[1], p[2]);
          return c === null ? "varió" : c >= 0 ? "creció" : "se redujo";
        }
        case "conc": {
          // {{conc:ind:corte:n}} participación de las n entidades más grandes en el total del universo
          var vals = D.entidades.map(function (e) { return valor(p[1], e.id, p[2]) || 0; }).sort(function (a, b) { return b - a; });
          var tot = vals.reduce(function (a, b) { return a + b; }, 0), n0 = +(p[3] || 1);
          return fmt(tot ? vals.slice(0, n0).reduce(function (a, b) { return a + b; }, 0) / tot : null, "pct");
        }
        case "rank": {
          // {{rank:ind:ent:corte}} posición de la entidad dentro del universo
          var ord = D.entidades.map(function (e) { return { e: e.id, v: valor(p[1], e.id, p[3]) }; })
            .filter(function (x) { return x.v; }).sort(function (a, b) { return b.v - a.v; });
          var i0 = ord.findIndex(function (x) { return x.e === p[2]; });
          return i0 < 0 ? "n.d." : String(i0 + 1);
        }
        case "crec_rel": {
          // {{crec_rel:ind:ent:comparador}} diferencia de crecimiento anual en puntos porcentuales
          var c1 = crec(p[1], p[2]), c2 = crec(p[1], p[3]);
          return fmt(c1 !== null && c2 !== null ? c1 - c2 : null, "pp");
        }
        case "veces": {
          // {{veces:ind:ent:comparador}} cuántas veces creció más rápido ent que el comparador
          var x1 = crec(p[1], p[2]), x2 = crec(p[1], p[3]);
          return x1 !== null && x2 ? new Intl.NumberFormat("es-CO", { maximumFractionDigits: 1 }).format(x1 / x2) : "n.d.";
        }
        case "mas_crec": {
          // {{mas_crec:ind}} entidad con mayor crecimiento anual (con base > 0)
          var cr = D.entidades.map(function (e) { return { e: e.id, c: crec(p[1], e.id) }; })
            .filter(function (x) { return x.c !== null && isFinite(x.c); }).sort(function (a, b) { return b.c - a.c; });
          return cr.length ? NOMBRES[cr[0].e] : "n.d.";
        }
        case "lider": case "n_ent": {
          // {{lider:ind:corte}} entidad con mayor valor; {{n_ent:ind:corte}} entidades con dato > 0
          var con = D.entidades.map(function (e) { return { e: e.id, v: valor(p[1], e.id, p[2]) }; })
            .filter(function (x) { return x.v; }).sort(function (a, b) { return b.v - a.v; });
          if (op === "n_ent") return String(con.length);
          return con.length ? NOMBRES[con[0].e] : "n.d.";
        }
        case "fecha": return fmtFecha(D.ultimo[p[1]]);
        case "nombre": return NOMBRES[p[1]] || p[1];
        case "corte": return fmtFecha(D.meta.corte_informe);
        case "base": return fmtFecha(D.meta.corte_base);
        case "anio": return String(anioInforme());
        case "csv": return BASE + "data/indicadores.csv";
        default: return "{{" + expr + "}}";
      }
    } catch (e) { return "n.d."; }
  }
  function rellenar(md) {
    return md.replace(/\{\{([^}]+)\}\}/g, function (_, e) { return marcador(e); });
  }

  // ------------------------------------------------------------- gráficas
  function entidadesDe(spec, ind, fecha) {
    var lista = spec.entidades;
    if (!lista || lista === "todas") {
      lista = D.entidades.filter(function (e) { return !spec.grupo || e.grupo === spec.grupo; })
        .map(function (e) { return e.id; });
    }
    return lista;
  }
  function valorSpec(spec, ent, fecha) {
    if (spec.crec) return crec(spec.indicador, ent);
    if (spec.crec_anual) return crecAnual(spec.indicador, ent);
    if (spec.ratio) {
      var n = valor(spec.ratio[0], ent, fecha), d = valor(spec.ratio[1], ent, fecha);
      return n !== null && d ? n / d : null;
    }
    if (spec.anual) return anual(spec.indicador, ent, spec.anual === "informe" ? anioInforme() : spec.anual);
    return valor(spec.indicador, ent, fecha);
  }

  function opcionesBase(spec) {
    return {
      color: PALETA,
      textStyle: { fontFamily: "inherit", color: COLOR.cuerpo },
      grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true },
      tooltip: { trigger: "axis", valueFormatter: function (v) { return fmt(v, spec.formato); } },
      legend: { top: 0, type: "scroll", textStyle: { color: COLOR.cuerpo } },
    };
  }

  function barras(spec) {
    var f = spec.fecha || "informe", ind = spec.indicador || (spec.ratio && spec.ratio[0]);
    var ents = entidadesDe(spec, ind, f);
    var datos = ents.map(function (e) { return { e: e, v: valorSpec(spec, e, f) }; })
      .filter(function (x) { return x.v !== null && (spec.incluir_ceros || x.v !== 0); });
    if (spec.orden !== "fijo") datos.sort(function (a, b) { return b.v - a.v; });
    var comp = (spec.comparadores || []).map(function (c) { return { name: NOMBRES[c] || c, v: valorSpec(spec, c, f) }; });
    var o = opcionesBase(spec);
    o.legend.show = false;
    o.tooltip.trigger = "item";
    o.yAxis = { type: "category", inverse: true, data: datos.map(function (x) { return NOMBRES[x.e] || x.e; }),
      axisTick: { show: false }, axisLine: { lineStyle: { color: COLOR.linea } } };
    o.xAxis = { type: "value", axisLabel: { formatter: eje(spec.formato) }, splitLine: { lineStyle: { color: COLOR.linea } } };
    o.series = [{ type: "bar", data: datos.map(function (x) { return x.v; }), itemStyle: { color: COLOR.navy, borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: "right", formatter: function (p) { return eje(spec.formato)(p.value); }, color: COLOR.cuerpo, fontSize: 11 },
      markLine: comp.length ? { symbol: "none", label: { formatter: function (p) { return p.name; }, color: COLOR.suave, fontSize: 11 },
        lineStyle: { color: COLOR.terracotta, type: "dashed" }, data: comp.filter(function (c) { return c.v !== null; })
          .map(function (c) { return { name: c.name, xAxis: c.v }; }) } : undefined }];
    o.grid.right = 48;
    return { o: o, alto: Math.max(220, 34 * datos.length + 60), fecha: resolverFecha(ind, f) };
  }

  function lineas(spec) {
    var ents = entidadesDe(spec), fechas = {}, desde = spec.desde || "0000";
    var series = ents.map(function (e) {
      // part_de: participación de la entidad en un comparador (p. ej. sis_ec) mes a mes.
      var pares = spec.part_de
        ? serie(spec.indicador, e).map(function (p) { var d = valor(spec.indicador, spec.part_de, p[0]); return [p[0], d ? p[1] / d : null]; })
        : spec.ratio
        ? serie(spec.ratio[0], e).map(function (p) { var d = valor(spec.ratio[1], e, p[0]); return [p[0], d ? p[1] / d : null]; })
        : serie(spec.indicador, e);
      pares = pares.filter(function (p) { return p[0] >= desde; });
      pares.forEach(function (p) { fechas[p[0]] = 1; });
      return { name: NOMBRES[e] || e, type: "line", showSymbol: false, smooth: false, data: pares, connectNulls: true,
        lineStyle: { width: e === ents[0] ? 3 : 2 } };
    }).filter(function (s) { return s.data.length; });
    var o = opcionesBase(spec);
    o.xAxis = { type: "time", axisLabel: { formatter: function (v) { var d = new Date(v); return MESES[d.getMonth()] + "\n" + d.getFullYear(); } },
      axisLine: { lineStyle: { color: COLOR.linea } } };
    o.yAxis = { type: "value", axisLabel: { formatter: eje(spec.formato) }, splitLine: { lineStyle: { color: COLOR.linea } }, scale: !!spec.escala_libre };
    o.series = series;
    var ult = Object.keys(fechas).sort().pop();
    return { o: o, alto: 340, fecha: ult };
  }

  function apiladas(spec) {
    // Una barra por entidad, apilando varios indicadores (p. ej. depósitos por producto).
    var f = spec.fecha || "informe", ents = entidadesDe(spec);
    var tot = ents.map(function (e) {
      return spec.indicadores.reduce(function (a, i) { return a + (valor(i.id, e, f) || 0); }, 0);
    });
    var orden = ents.map(function (e, i) { return { e: e, t: tot[i] }; }).filter(function (x) { return x.t > 0; })
      .sort(function (a, b) { return b.t - a.t; });
    // Comparadores (p. ej. sis_ec) al final, para contrastar la composición con el sistema.
    (spec.comparadores || []).forEach(function (c) {
      var t = spec.indicadores.reduce(function (a, i) { return a + (valor(i.id, c, f) || 0); }, 0);
      if (t > 0) orden.push({ e: c, t: t });
    });
    var o = opcionesBase(spec);
    o.tooltip.trigger = "axis";
    o.yAxis = { type: "category", inverse: true, data: orden.map(function (x) { return NOMBRES[x.e] || x.e; }), axisTick: { show: false } };
    o.xAxis = { type: "value", axisLabel: { formatter: eje(spec.proporcion ? "pct" : spec.formato) }, splitLine: { lineStyle: { color: COLOR.linea } }, max: spec.proporcion ? 1 : null };
    o.series = spec.indicadores.map(function (i) {
      return { name: i.nombre, type: "bar", stack: "t", data: orden.map(function (x) {
        var v = valor(i.id, x.e, f) || 0; return spec.proporcion ? v / x.t : v; }) };
    });
    if (spec.proporcion) o.tooltip.valueFormatter = function (v) { return fmt(v, "pct"); };
    return { o: o, alto: Math.max(240, 34 * orden.length + 70), fecha: resolverFecha(spec.indicadores[0].id, f) };
  }

  function rangos(spec) {
    var t = D.tablas.rangos_saldo || {}, fechas = Object.keys(t).sort();
    var f = spec.fecha === "ultimo" ? fechas[fechas.length - 1] : (fechas.indexOf(D.meta.corte_informe) >= 0 ? D.meta.corte_informe : fechas[fechas.length - 1]);
    var filas = t[f] || [], total = filas.reduce(function (a, r) { return a + r.cuentas; }, 0);
    var o = opcionesBase({ formato: "pct" });
    o.legend.show = false; o.tooltip.trigger = "item";
    o.xAxis = { type: "category", data: filas.map(function (r) { return r.rango.replace(" SMMLV", ""); }), axisLabel: { rotate: 30, fontSize: 10 } };
    o.yAxis = { type: "value", axisLabel: { formatter: eje("pct") }, splitLine: { lineStyle: { color: COLOR.linea } } };
    o.series = [{ type: "bar", data: filas.map(function (r) { return total ? r.cuentas / total : 0; }), itemStyle: { color: COLOR.navy, borderRadius: [6, 6, 0, 0] } }];
    o.tooltip.valueFormatter = function (v) { return fmt(v, "pct"); };
    return { o: o, alto: 320, fecha: f };
  }

  function canales(spec) {
    var t = D.tablas.canales || {}, fechas = Object.keys(t).sort(), f = fechas[fechas.length - 1];
    var filas = t[f] || [], porCanal = {};
    filas.forEach(function (r) { porCanal[r.canal] = (porCanal[r.canal] || 0) + (r[spec.medida || "cantidad"] || 0); });
    var datos = Object.keys(porCanal).map(function (k) { return { name: k, value: porCanal[k] }; }).sort(function (a, b) { return b.value - a.value; });
    var o = opcionesBase({ formato: spec.formato });
    o.legend.show = false; o.tooltip.trigger = "item";
    o.yAxis = { type: "category", inverse: true, data: datos.map(function (d) { return d.name; }), axisTick: { show: false } };
    o.xAxis = { type: "value", axisLabel: { formatter: eje(spec.formato) }, splitLine: { lineStyle: { color: COLOR.linea } } };
    o.series = [{ type: "bar", data: datos.map(function (d) { return d.value; }), itemStyle: { color: COLOR.navy, borderRadius: [0, 6, 6, 0] } }];
    return { o: o, alto: Math.max(240, 30 * datos.length + 60), fecha: f };
  }

  function tablaEntidades() {
    var filas = D.entidades.map(function (e) {
      return "<tr><td><strong>" + e.marca + "</strong></td><td>" + D.grupos[e.grupo] + "</td><td>" + e.licencia +
        "</td><td>" + (e.fecha_autorizacion || "Por confirmar") + (e.licencia_2026 ? " (licencia 2026)" : "") + "</td></tr>";
    }).join("");
    return '<div class="cfn-tabla"><table><thead><tr><th>Entidad</th><th>Grupo</th><th>Licencia</th><th>Autorización</th></tr></thead><tbody>' +
      filas + "</tbody></table></div>";
  }

  function cdtPlazos(spec) {
    // Tasa promedio de los CDT emitidos por plazo: universo vs. establecimientos de crédito (mes indicado o último).
    var t = D.tablas.cdt_plazos || {}, fechas = Object.keys(t).sort();
    var f = spec.fecha === "informe" && t[D.meta.corte_informe] ? D.meta.corte_informe : fechas[fechas.length - 1];
    var filas = (t[f] || []).filter(function (r) { return r.tasa_s !== null; });
    var o = opcionesBase({ formato: "tasa" });
    o.xAxis = { type: "category", data: filas.map(function (r) { return r.plazo.replace("Entre ", "").replace(" Dias", " d").replace("A ", ""); }), axisLabel: { rotate: 35, fontSize: 10 } };
    o.yAxis = { type: "value", axisLabel: { formatter: eje("tasa") }, splitLine: { lineStyle: { color: COLOR.linea } }, scale: true };
    o.series = [
      { name: "Neobancos y billeteras", type: "bar", data: filas.map(function (r) { return r.tasa_u; }), itemStyle: { color: COLOR.navy } },
      { name: "Establecimientos de crédito", type: "bar", data: filas.map(function (r) { return r.tasa_s; }), itemStyle: { color: COLOR.sage } },
    ];
    return { o: o, alto: 340, fecha: f };
  }

  function fichas() {
    // Una tarjeta por entidad con sus cifras principales al corte del informe.
    var g = function (ind, e) { return valor(ind, e, "informe"); };
    var cards = D.entidades.filter(function (e) { return g("activo", e.id); })
      .sort(function (a, b) { return g("activo", b.id) - g("activo", a.id); })
      .map(function (e) {
        var cli = Math.max(g("clientes_ahorro", e.id) || 0, g("clientes_depelec", e.id) || 0);
        var util = g("utilidad", e.id), pat = g("patrimonio", e.id), c = crec("activo", e.id);
        var kpi = [
          ["Activos", fmt(g("activo", e.id), "milm").replace(" mil millones", " mm")],
          ["Crec. activos", c === null || !isFinite(c) ? "n.d." : fmt(c, "pct")],
          ["Depósitos", fmt(g("depositos_total", e.id), "milm").replace(" mil millones", " mm")],
          ["Cartera", g("cartera_bruta", e.id) ? fmt(g("cartera_bruta", e.id), "milm").replace(" mil millones", " mm") : "—"],
          ["Clientes de depósito", cli ? fmt(cli, cli < 1e5 ? "miles" : "millones") : "—"],
          ["Resultado del año", util === null ? "n.d." : (util >= 0 ? "Utilidad" : "Pérdida") + (pat ? " (" + fmt(util / pat, "pct") + " del patrimonio)" : "")],
          ["Solvencia", g("solvencia", e.id) ? fmt(g("solvencia", e.id), "tasa").replace(" E.A.", "") : "n.d."],
        ];
        return '<div class="cfn-ficha"><div class="cfn-ficha-h"><b>' + e.marca + "</b><span>" + D.grupos[e.grupo] + "</span></div><dl>" +
          kpi.map(function (k) { return "<dt>" + k[0] + "</dt><dd>" + k[1] + "</dd>"; }).join("") + "</dl></div>";
      }).join("");
    return '<div class="cfn-fichas">' + cards + '</div><p class="cfn-nota">Cifras a ' + fmtFecha(D.meta.corte_informe) +
      ". mm = miles de millones de pesos. Clientes de depósito: el mayor entre ahorro y depósitos electrónicos. Solvencia: relación de solvencia total.</p>";
  }

  var TIPOS = { barras: barras, lineas: lineas, apiladas: apiladas, rangos: rangos, canales: canales, cdt_plazos: cdtPlazos };

  function csvDe(chart) {
    var o = chart.getOption(), lineasCsv = [];
    if (o.yAxis && o.yAxis[0] && o.yAxis[0].type === "category") {
      lineasCsv.push(["categoria"].concat(o.series.map(function (s) { return s.name || "valor"; })).join(","));
      o.yAxis[0].data.forEach(function (c, i) {
        lineasCsv.push(['"' + c + '"'].concat(o.series.map(function (s) { var v = s.data[i]; return v && v.value !== undefined ? v.value : v; })).join(","));
      });
    } else if (o.xAxis && o.xAxis[0] && o.xAxis[0].type === "category") {
      lineasCsv.push("categoria,valor");
      o.xAxis[0].data.forEach(function (c, i) { lineasCsv.push('"' + c + '",' + o.series[0].data[i]); });
    } else {
      lineasCsv.push("serie,fecha,valor");
      o.series.forEach(function (s) { s.data.forEach(function (p) { lineasCsv.push('"' + s.name + '",' + p[0] + "," + p[1]); }); });
    }
    return lineasCsv.join("\n");
  }

  function montarGrafica(nodo, spec) {
    if (spec.tipo === "tabla_entidades") { nodo.outerHTML = tablaEntidades(); return; }
    if (spec.tipo === "fichas") { nodo.outerHTML = fichas(); return; }
    var r = TIPOS[spec.tipo](spec);
    var fig = document.createElement("figure");
    fig.className = "cfn-fig";
    var fuente = spec.fuente || D.fuente_indicador[spec.indicador || (spec.ratio && spec.ratio[0]) || (spec.indicadores && spec.indicadores[0].id)] ||
      (spec.tipo === "rangos" ? "SFC, captaciones por rangos" : spec.tipo === "canales" ? "SFC, operaciones por canal (formato 444)" : "");
    fig.innerHTML = '<figcaption class="cfn-tit">' + (spec.titulo || "") + "</figcaption>" +
      (spec.formato || spec.proporcion ? '<div class="cfn-unidad">' + (spec.proporcion ? "Participación (%)" : (spec.unidad || UNIDAD[spec.formato] || "")) + "</div>" : "") +
      '<div class="cfn-canvas" style="height:' + r.alto + 'px"></div>' +
      '<div class="cfn-pie"><span>Fuente: ' + fuente + ". Corte: " + fmtFecha(r.fecha) + "." + (spec.nota ? " " + spec.nota : "") +
      '</span><button type="button" class="cfn-csv">Descargar CSV</button></div>';
    nodo.replaceWith(fig);
    var ch = window.echarts.init(fig.querySelector(".cfn-canvas"), null, { renderer: "svg" });
    ch.setOption(r.o);
    new ResizeObserver(function () { ch.resize(); }).observe(fig);
    fig.querySelector(".cfn-csv").addEventListener("click", function () {
      var a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob(["﻿" + csvDe(ch)], { type: "text/csv" }));
      a.download = (spec.id || spec.indicador || "grafica") + ".csv"; a.click();
    });
  }

  // --------------------------------------------------------------- render
  var CSS = "" +
    // Fondo propio (papel): el informe se lee igual sobre un tema claro u oscuro del sitio.
    "#cf-neobancos{--navy:#2B3241;--mint:#ADD5C2;--linea:#E1E3DD;--cuerpo:#4A505D;--papel:#F6F7F4;color:var(--cuerpo);background:var(--papel);border-radius:28px;padding:24px;line-height:1.6;max-width:1008px;margin:0 auto}" +
    "#cf-neobancos *{box-sizing:border-box}" +
    "#cf-neobancos p,#cf-neobancos li,#cf-neobancos td,#cf-neobancos span{color:var(--cuerpo)}" +
    "#cf-neobancos strong,#cf-neobancos b{color:var(--navy)}" +
    "#cf-neobancos a{color:var(--navy);text-decoration:underline}" +
    "#cf-neobancos table{background:transparent}#cf-neobancos tr{background:transparent!important}" +
    "#cf-neobancos h2,#cf-neobancos h3{color:var(--navy);line-height:1.25}" +
    "#cf-neobancos h2{margin:2.4em 0 .6em;font-size:1.7em}#cf-neobancos h3{margin:1.6em 0 .4em;font-size:1.2em}" +
    "#cf-neobancos .cfn-head{background:var(--mint);border-radius:24px;padding:28px 28px 22px;color:var(--navy)}" +
    "#cf-neobancos .cfn-head h1{margin:0 0 .3em;font-size:2em;line-height:1.15;color:var(--navy)}" +
    "#cf-neobancos .cfn-meta{font-size:.85em;opacity:.85}" +
    "#cf-neobancos .cfn-toc{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0;padding:0;list-style:none}" +
    "#cf-neobancos .cfn-toc a{display:inline-block;padding:4px 12px;border-radius:999px;background:#fff;color:var(--navy);text-decoration:none;font-size:.85em}" +
    "#cf-neobancos .cfn-cifras{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:20px 0}" +
    "#cf-neobancos .cfn-cifra{background:#fff;border:1.5px solid var(--linea);border-radius:18px;padding:16px}" +
    "#cf-neobancos .cfn-cifra b{display:block;font-size:1.5em;color:var(--navy);line-height:1.2}" +
    "#cf-neobancos .cfn-cifra span{font-size:.85em}" +
    "#cf-neobancos .cfn-fig{margin:24px 0;padding:18px;background:#fff;border:1.5px solid var(--linea);border-radius:24px}" +
    "#cf-neobancos .cfn-tit{font-weight:700;color:var(--navy);font-size:1.05em}" +
    "#cf-neobancos .cfn-unidad{font-size:.8em;color:#6B707B;margin-bottom:6px}" +
    "#cf-neobancos .cfn-pie{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;font-size:.78em;color:#6B707B;margin-top:8px}" +
    "#cf-neobancos .cfn-csv{border:1.5px solid var(--linea);background:var(--papel);color:var(--navy);border-radius:999px;padding:4px 12px;cursor:pointer;font:inherit;white-space:nowrap}" +
    "#cf-neobancos .cfn-tabla{overflow-x:auto;margin:20px 0}" +
    "#cf-neobancos table{border-collapse:collapse;width:100%;font-size:.9em}" +
    "#cf-neobancos th,#cf-neobancos td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--linea)}" +
    "#cf-neobancos th{color:var(--navy)}" +
    "#cf-neobancos .cfn-fichas{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:20px 0}" +
    "#cf-neobancos .cfn-ficha{background:#fff;border:1.5px solid var(--linea);border-radius:18px;padding:14px 16px}" +
    "#cf-neobancos .cfn-ficha-h{border-bottom:1px solid var(--linea);padding-bottom:6px;margin-bottom:6px}" +
    "#cf-neobancos .cfn-ficha-h b{display:block;font-size:1.05em}#cf-neobancos .cfn-ficha-h span{font-size:.75em;color:#6B707B}" +
    "#cf-neobancos .cfn-ficha dl{display:grid;grid-template-columns:auto 1fr;gap:3px 10px;margin:0;font-size:.82em}" +
    "#cf-neobancos .cfn-ficha dt{color:#6B707B}#cf-neobancos .cfn-ficha dd{margin:0;text-align:right;color:var(--navy);font-weight:600}" +
    "#cf-neobancos .cfn-nota{font-size:.82em;color:#6B707B}" +
    "#cf-neobancos .cfn-error{padding:16px;border-radius:12px;background:#fdf1ec}" +
    "@media (max-width:600px){#cf-neobancos{padding:12px;border-radius:20px}#cf-neobancos .cfn-head{padding:20px 16px}#cf-neobancos .cfn-head h1{font-size:1.5em}#cf-neobancos .cfn-fig{padding:12px}#cf-neobancos .cfn-pie{flex-direction:column}}";

  function cifras(lista) {
    // ```cifras  [{"valor":"{{...}}","texto":"..."}]```
    return '<div class="cfn-cifras">' + lista.map(function (c) {
      return '<div class="cfn-cifra"><b>' + rellenar(c.valor) + "</b><span>" + rellenar(c.texto) + "</span></div>";
    }).join("") + "</div>";
  }

  function render(raiz) {
    D.entidades.forEach(function (e) { NOMBRES[e.id] = e.marca; });
    D.comparadores.forEach(function (c) { NOMBRES[c.id] = c.nombre; });
    Object.keys(D.grupos).forEach(function (g) { NOMBRES["grupo_" + g] = D.grupos[g]; });
    NOMBRES.universo = "Neobancos y billeteras (total)";

    var specs = [], html = "";
    D.secciones.forEach(function (s) {
      var md = s.md.replace(/```(grafico|cifras)\s*\n([\s\S]*?)```/g, function (_, tipo, cuerpo) {
        var json = JSON.parse(cuerpo);
        if (tipo === "cifras") return cifras(json);
        specs.push(json);
        return '<div class="cfn-graf" data-i="' + (specs.length - 1) + '"></div>';
      });
      html += '<section id="cfn-' + s.id + '">' + window.marked.parse(rellenar(md)) + "</section>";
    });
    var toc = D.secciones.filter(function (s) { return s.titulo; }).map(function (s) {
      return '<li><a href="#cfn-' + s.id + '">' + s.titulo + "</a></li>";
    }).join("");
    raiz.innerHTML = '<header class="cfn-head"><h1>' + D.meta.titulo + '</h1><div class="cfn-meta">Datos de la Superintendencia Financiera de Colombia y Fogafín. Corte anual: ' +
      fmtFecha(D.meta.corte_informe) + ". Actualizado automáticamente el " + new Date(D.meta.generado).toLocaleDateString("es-CO", { day: "numeric", month: "long", year: "numeric" }) +
      '.</div><ul class="cfn-toc">' + toc + "</ul></header>" + html;
    raiz.querySelectorAll(".cfn-graf").forEach(function (n) {
      try { montarGrafica(n, specs[+n.getAttribute("data-i")]); }
      catch (e) { n.outerHTML = '<div class="cfn-error">No se pudo dibujar esta gráfica.</div>'; console.error(e); }
    });
  }

  function iniciar() {
    var raiz = document.getElementById("cf-neobancos");
    if (!raiz) return;
    var st = document.createElement("style"); st.textContent = CSS; document.head.appendChild(st);
    raiz.innerHTML = "<p>Cargando informe…</p>";
    Promise.all([
      window.echarts ? 0 : cargar(CDN.echarts),
      window.marked ? 0 : cargar(CDN.marked),
      fetch(BASE + "data/informe.json", { cache: "no-cache" }).then(function (r) { return r.json(); }),
    ]).then(function (res) { D = res[2]; render(raiz); })
      .catch(function (e) { console.error(e); raiz.innerHTML = '<div class="cfn-error">No fue posible cargar los datos del informe.</div>'; });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar); else iniciar();
})();
