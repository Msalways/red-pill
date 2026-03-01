# Redpill Chart Specification Documentation

## Overview

Redpill generates chart specifications from natural language prompts and transforms data using the executor. The specification is library-agnostic, meaning it can be rendered by any charting library (Recharts, Chart.js, ApexCharts, Apache ECharts).

---

## Spec Schema

### Full Specification Structure

```json
{
  "spec": {
    "version": "1.0",
    "chartType": "bar|horizontal_bar|line|area|pie|donut|scatter|bubble|radar|gauge|funnel|heatmap|treemap|waterfall|candlestick|polar",
    "xAxis": {
      "field": "field_name",
      "label": "Display Label",
      "type": "categorical|quantitative|time"
    },
    "yAxis": {
      "field": "count|field_name",
      "label": "Display Label",
      "aggregation": "count|sum|avg|min|max"
    },
    "series": {
      "field": "field_name",
      "label": "Display Label"
    } | null,
    "options": {
      "title": "Chart Title",
      "stacked": false,
      "orientation": "vertical|horizontal",
      "innerRadius": 50,
      "bubbleSize": 20,
      "showLegend": true,
      "showGrid": true,
      "colors": ["#color1", "#color2"]
    }
  },
  "params": {
    "timeField": "date_field" | null,
    "timeRange": {
      "type": "relative|absolute",
      "value": 2,
      "unit": "days|weeks|months|hours|minutes",
      "start": "2026-01-01",
      "end": "2026-01-31"
    },
    "filters": [
      { "field": "status", "operator": "eq", "value": "completed" }
    ],
    "limit": 10,
    "sort": { "field": "count", "direction": "desc" }
  }
}
```

---

## Supported Chart Types

| Type | Description | Best For | Libraries Supported |
|------|-------------|----------|---------------------|
| `bar` | Vertical bars | Category comparisons | All |
| `horizontal_bar` | Horizontal bars | Many categories | All |
| `line` | Line chart | Trends over time | All |
| `area` | Filled line | Volume trends | All |
| `pie` | Pie chart | Distribution/proportion | All |
| `donut` | Pie with hole | Modern distribution | All |
| `scatter` | X-Y points | Correlation | Recharts, ApexCharts, ECharts |
| `bubble` | Scatter with size | 3-variable data | ECharts |
| `radar` | Spider web | Multi-metric comparison | All |
| `gauge` | Dial/progress | Percentage display | ApexCharts, ECharts |
| `funnel` | Funnel shape | Pipeline/conversion | ECharts |
| `heatmap` | Color matrix | Density/intensity | ECharts |
| `treemap` | Nested rectangles | Hierarchical data | ECharts |
| `waterfall` | Sequential bars | Flow/changes | ECharts |
| `candlestick` | OHLC bars | Financial data | ECharts |
| `polar` | Polar area | Cyclical data | ECharts |

---

## Data Transformation Flow

### 1. Input Data (JSON)

```json
{
  "transactions": [
    { "type": "income", "category": "Sales", "amount": 15000, "date": "2026-02-25" },
    { "type": "expense", "category": "Rent", "amount": 5000, "date": "2026-02-24" }
  ]
}
```

### 2. After Executor Processing

The executor applies filters, time ranges, and groupings to produce:

```json
[
  { "x": "Sales", "y": 15000, "label_x": "Category", "label_y": "Amount" },
  { "x": "Rent", "y": 5000, "label_x": "Category", "label_y": "Amount" }
]
```

### 3. Chart Data Format

The standardized chart data format:

```typescript
interface ChartData {
  x: string | number;      // X-axis value (category, date, etc.)
  y: number;              // Y-axis value (count, sum, etc.)
  series?: string;        // Grouping for multi-series charts
  label_x?: string;       // X-axis label
  label_y?: string;       // Y-axis label
  label_series?: string;  // Series label
}
```

---

## Library-Specific Conversion Logic

### Recharts

```typescript
// Data transformation for Recharts
const formattedData = chartData.map(d => ({
  name: d.x,        // X-axis value as 'name'
  value: d.y,        // Y-axis value as 'value'
  series: d.series   // Series grouping
}));

// Chart type mapping
const rechartsType = {
  'bar': BarChart,
  'horizontal_bar': BarChart, // with layout="vertical"
  'line': LineChart,
  'area': AreaChart,
  'pie': PieChart,
  'donut': PieChart, // with innerRadius prop
  'scatter': ScatterChart,
  'radar': RadarChart
};
```

### Chart.js

```typescript
// Data transformation for Chart.js
const labels = chartData.map(d => d.x);
const values = chartData.map(d => d.y);

// Chart type mapping
const chartJsType = {
  'bar': 'bar',
  'horizontal_bar': 'bar', // with indexAxis: 'y'
  'line': 'line',
  'area': 'line', // with fill: true
  'pie': 'pie',
  'donut': 'doughnut', // with cutout: '60%'
  'radar': 'radar'
};

// Configuration
const chartConfig = {
  type: chartJsType[chartType],
  data: {
    labels,
    datasets: [{
      label: metadata.yAxis?.label,
      data: values,
      backgroundColor: colors,
      borderColor: colors[0],
      fill: chartType === 'area'
    }]
  },
  options: {
    responsive: true,
    indexAxis: chartType === 'horizontal_bar' ? 'y' : 'x'
  }
};
```

### ApexCharts

```typescript
// Data transformation for ApexCharts
const labels = chartData.map(d => d.x);
const values = chartData.map(d => d.y);

// Chart type mapping
const apexType = {
  'bar': 'bar',
  'horizontal_bar': 'bar',
  'line': 'line',
  'area': 'area',
  'pie': 'pie',
  'donut': 'donut',
  'scatter': 'scatter',
  'radar': 'radar'
};

// Options configuration
const apexOptions = {
  chart: { type: apexType[chartType], height: 400 },
  colors: ['#4F46E5', '#10B981', ...],
  labels,
  xaxis: { categories: labels },
  plotOptions: {
    pie: { donut: { size: '65%' } }
  }
};
```

### Apache ECharts (Most Comprehensive)

```typescript
// ECharts has the most flexible configuration
const eChartsOption = {
  // Base structure
  tooltip: { trigger: 'axis' },
  legend: { data: ['Value'] },
  grid: { containLabel: true },
  
  // Type-specific configurations
  ...(chartType === 'pie' || chartType === 'donut' ? {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: chartType === 'donut' ? ['40%', '70%'] : '55%',
      data: chartData.map(d => ({ value: d.y, name: d.x }))
    }]
  } : {}),
  
  ...(chartType === 'gauge' ? {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      progress: { show: true, width: 18 },
      data: [{ value: values[0], name: 'Score' }]
    }]
  } : {}),
  
  ...(chartType === 'funnel' ? {
    series: [{
      type: 'funnel',
      sort: 'descending',
      data: chartData.map(d => ({ value: d.y, name: d.x }))
    }]
  } : {}),
  
  ...(chartType === 'treemap' ? {
    series: [{
      type: 'treemap',
      data: chartData.map(d => ({ value: d.y, name: d.x }))
    }]
  } : {}),
  
  // Default axis-based charts
  ...(['bar', 'line', 'area', 'horizontal_bar'].includes(chartType) ? {
    xAxis: { type: chartType === 'horizontal_bar' ? 'value' : 'category', data: labels },
    yAxis: { type: chartType === 'horizontal_bar' ? 'category' : 'value', data: labels },
    series: [{ type: chartType === 'horizontal_bar' ? 'bar' : chartType, data: values }]
  } : {})
};
```

---

## Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `{ "field": "status", "operator": "eq", "value": "completed" }` |
| `ne` | Not equals | `{ "field": "status", "operator": "ne", "value": "pending" }` |
| `gt` | Greater than | `{ "field": "amount", "operator": "gt", "value": 10000 }` |
| `gte` | Greater or equal | `{ "field": "amount", "operator": "gte", "value": 1000 }` |
| `lt` | Less than | `{ "field": "priority", "operator": "lt", "value": 5 }` |
| `lte` | Less or equal | `{ "field": "count", "operator": "lte", "value": 100 }` |
| `in` | In array | `{ "field": "type", "operator": "in", "value": ["income", "expense"] }` |
| `not_in` | Not in array | `{ "field": "status", "operator": "not_in", "value": ["cancelled"] }` |
| `contains` | String contains | `{ "field": "name", "operator": "contains", "value": "test" }` |

---

## Time Range Configuration

### Relative Time

```json
{
  "timeField": "date",
  "timeRange": {
    "type": "relative",
    "value": 2,
    "unit": "days"
  }
}
```

Supported units: `minutes`, `hours`, `days`, `weeks`, `months`

### Absolute Time

```json
{
  "timeField": "date",
  "timeRange": {
    "type": "absolute",
    "start": "2026-01-01",
    "end": "2026-02-28"
  }
}
```

---

## Aggregation Types

| Type | Description | Use Case |
|------|-------------|----------|
| `count` | Count of records | Default for most charts |
| `sum` | Sum of values | Total amounts |
| `avg` | Average value | Mean calculations |
| `min` | Minimum value | Finding lows |
| `max` | Maximum value | Finding peaks |

---

## Example Prompts and Specs

### Example 1: Simple Distribution

**Prompt:** "show me transactions by type"

```json
{
  "spec": {
    "chartType": "pie",
    "xAxis": { "field": "type", "label": "Transaction Type", "type": "categorical" },
    "yAxis": { "field": "count", "label": "Count", "aggregation": "count" },
    "series": null,
    "options": { "title": "Transactions by Type" }
  },
  "params": { "filters": [] }
}
```

### Example 2: Filtered Trend

**Prompt:** "show me income transactions by category in last week"

```json
{
  "spec": {
    "chartType": "bar",
    "xAxis": { "field": "category", "label": "Category", "type": "categorical" },
    "yAxis": { "field": "count", "label": "Count", "aggregation": "count" },
    "series": null,
    "options": { "title": "Income by Category (Last Week)" }
  },
  "params": {
    "timeField": "date",
    "timeRange": { "type": "relative", "value": 1, "unit": "weeks" },
    "filters": [
      { "field": "type", "operator": "eq", "value": "income" }
    ]
  }
}
```

### Example 3: Multi-Series Comparison

**Prompt:** "show me deals by stage with owner breakdown"

```json
{
  "spec": {
    "chartType": "bar",
    "xAxis": { "field": "stage", "label": "Stage", "type": "categorical" },
    "yAxis": { "field": "count", "label": "Count", "aggregation": "count" },
    "series": { "field": "owner", "label": "Owner" },
    "options": { "title": "Deals by Stage", "stacked": true }
  },
  "params": { "filters": [] }
}
```

---

## Error Handling

The executor includes edge case handling:

1. **Case-insensitive filters**: String comparisons are normalized to lowercase
2. **Multiple date formats**: Supports `YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`, etc.
3. **Missing fields**: Silently skips invalid filters
4. **Empty results**: Returns warning in metadata
5. **Type coercion**: Handles type mismatches gracefully

---

## Metadata Response

The executor returns metadata with the chart data:

```json
{
  "chartData": [...],
  "metadata": {
    "chartType": "bar",
    "xAxis": { "field": "category", "label": "Category" },
    "yAxis": { "field": "count", "label": "Count" },
    "series": { "field": "status", "label": "Status" },
    "warnings": ["Filter resulted in empty dataset"],
    "originalCount": 150,
    "filteredCount": 45
  }
}
```

---

## Quick Reference

### Field Resolution

The executor automatically resolves field names:
- Exact match: `transactions.type` → `transactions.type`
- Without prefix: `transactions.type` → `type` (if exists)

### Color Palette

Default colors used across libraries:
```javascript
['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4']
```

### Chart Selection Guidelines

| User Intent | Recommended Chart |
|-------------|-------------------|
| "distribution", "proportion" | pie/donut |
| "compare", "by category" | bar |
| "trend", "over time" | line/area |
| "breakdown" | stacked bar |
| "progress", "percentage" | gauge |
| "stages", "pipeline" | funnel |
| "correlation" | scatter |
| "comparison" multiple metrics | radar |
