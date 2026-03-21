import pandas as pd
import json
import os

file_path = "data/data.xlsx"
df = pd.read_excel(file_path)
df = df.dropna(subset=['Source', 'Target'])

nodes_dict = {}
for idx, row in df.iterrows():
    # 数据中 Source 是被投公司，Target 是投资机构
    s = str(row['Source']).strip() # 被投公司
    t = str(row['Target']).strip() # 投资机构
    
    if t not in nodes_dict:
        # 0 代表 投资机构
        nodes_dict[t] = {'id': t, 'name': t, 'category': 0, 'value': 0}
    if s not in nodes_dict:
        # 1 代表 被投公司
        nodes_dict[s] = {'id': s, 'name': s, 'category': 1, 'value': 0}
        
    nodes_dict[t]['value'] += 1
    nodes_dict[s]['value'] += 1

nodes = list(nodes_dict.values())

import math
for n in nodes:
    # Scale node size based on degree
    n['symbolSize'] = min(max(math.sqrt(n['value']) * 6, 15), 60)

links = []
for idx, row in df.iterrows():
    s = str(row['Source']).strip() # 公司
    t = str(row['Target']).strip() # 机构
    # 为了 tooltip 变成 "机构 投资了 公司"，我们将 source 设为 t，target 设为 s
    links.append({'source': t, 'target': s})

data_json = json.dumps({'nodes': nodes, 'links': links}, ensure_ascii=False)

html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>工业机器人投资网络</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
    <style>
        body { margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #fcfcfc; color: #333; }
        #main { width: 100vw; height: 100vh; }
        #control-panel { position: absolute; top: 30px; left: 30px; background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); z-index: 10; width: 330px; }
        h2 { margin-top: 0; margin-bottom: 20px; font-size: 18px; color: #2c3e50; font-weight: 600; }
        .search-group { display: flex; gap: 10px; margin-bottom: 15px; }
        input[type=text] { flex: 1; padding: 10px 12px; border: 1px solid #dce0e4; border-radius: 6px; font-size: 14px; transition: border-color 0.2s; outline: none; }
        input[type=text]:focus { border-color: #7a9ea8; }
        button { padding: 10px 16px; background-color: #7a9ea8; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; transition: background 0.2s, transform 0.1s; }
        button:hover { background-color: #658891; }
        button:active { transform: scale(0.98); }
        .btn-reset { background-color: #aeb6bf; }
        .btn-reset:hover { background-color: #95a5a6; }
        .instruction { font-size: 13px; color: #7f8c8d; line-height: 1.5; margin-top: 15px; padding-top: 15px; border-top: 1px solid #edf2f7; }
        .legend-box { margin-top: 15px; display: flex; flex-direction: column; gap: 8px; }
        .legend-item { display: flex; align-items: center; font-size: 13px; color: #555; }
        .legend-color { width: 14px; height: 14px; border-radius: 50%; margin-right: 10px; }
        .note { margin-top: 12px; font-size: 12px; color: #b35900; background: #fff8eb; padding: 10px; border-radius: 6px; border-left: 3px solid #e67e22; }
    </style>
</head>
<body>
    <div id="control-panel">
        <h2>工业机器人投资网络</h2>
        <div class="search-group">
            <input type="text" id="searchInput" placeholder="搜索机构或公司名称...">
            <button onclick="searchNode()">搜索</button>
        </div>
        <button class="btn-reset" onclick="resetGraph()" style="width: 100%;">还原全部数据</button>
        
        <div class="legend-box">
            <div class="legend-item"><div class="legend-color" style="background-color: #7a9ea8;"></div> 投资机构 </div>
            <div class="legend-item"><div class="legend-color" style="background-color: #d8a08a;"></div> 被投公司 </div>
        </div>

        <div class="instruction">
            <strong>交互说明：</strong><br>
            • 点击任一节点：高亮自身及直接关联的对象，其余变为浅灰色。<br>
            • 点击空白区域：取消高亮，恢复默认显示。<br>
            • 鼠标滚轮缩放，拖拽平移画布。
            <div class="note">
                注：本图片仅包含45家工业机器人公司的投资事件情况，并非全部工业机器人投资事件
            </div>
        </div>
    </div>
    <div id="main"></div>
    <script>
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var rawData = __DATA_JSON__;

        var nodes = rawData.nodes;
        var links = rawData.links;

        var adjList = {};
        nodes.forEach(function(n) { adjList[n.id] = []; });
        links.forEach(function(l) {
            adjList[l.source].push(l.target);
            adjList[l.target].push(l.source);
        });

        var defaultNodeStyle = { category0: '#7a9ea8', category1: '#d8a08a' };
        var greyStyle = '#e8ebed'; 
        var greyLabel = '#cbd1d6';
        var greyLine = '#f0f2f5';

        var formattedNodes = nodes.map(function(n) {
            return Object.assign({}, n, {
                itemStyle: { color: n.category === 0 ? defaultNodeStyle.category0 : defaultNodeStyle.category1 },
                label: { show: n.category === 1, fontSize: 12, color: '#4a5568' }
            });
        });
        
        var formattedLinks = links.map(function(l) {
            return Object.assign({}, l, {
                lineStyle: { color: '#d1d8e0', curveness: 0.15, opacity: 0.8, width: 1 }
            });
        });

        var option = {
            tooltip: {
                formatter: function(params) {
                    if (params.dataType === 'node') {
                        var type = params.data.category === 0 ? '投资机构' : '被投公司';
                        var countLabel = params.data.category === 0 ? '出手次数' : '参投机构数';
                        return '<div style="font-weight:bold;margin-bottom:5px;">' + params.data.name + '</div>' + 
                               type + '<br/>' + countLabel + ': ' + params.data.value;
                    } else if (params.dataType === 'edge') {
                        return params.data.source + ' 投资了 ' + params.data.target;
                    }
                },
                backgroundColor: 'rgba(255,255,255,0.9)',
                borderColor: '#eee',
                textStyle: { color: '#333' }
            },
            series: [
                {
                    type: 'graph',
                    layout: 'force',
                    roam: true,
                    data: formattedNodes,
                    links: formattedLinks,
                    categories: [ { name: '投资机构' }, { name: '被投公司' } ],
                    label: { position: 'right', formatter: '{b}' },
                    force: { repulsion: Math.max(800, nodes.length * 5), gravity: 0.1, edgeLength: 60, layoutAnimation: true },
                    emphasis: { focus: 'none' }
                }
            ]
        };

        myChart.setOption(option);
        var isHighlighted = false;

        function highlightNodeAndNeighbors(nodeId) {
            var neighbors = adjList[nodeId];
            if (!neighbors) return;
            isHighlighted = true;
            
            var highlightMap = {};
            highlightMap[nodeId] = true;
            neighbors.forEach(function(neighborId) { highlightMap[neighborId] = true; });

            var newNodes = formattedNodes.map(function(n) {
                var isHigh = highlightMap[n.id];
                var color = n.category === 0 ? defaultNodeStyle.category0 : defaultNodeStyle.category1;
                return Object.assign({}, n, {
                    itemStyle: { color: isHigh ? color : greyStyle, borderColor: isHigh ? '#fff' : 'transparent', borderWidth: isHigh ? 2 : 0 },
                    label: { show: isHigh, color: isHigh ? '#2d3748' : greyLabel, fontWeight: isHigh ? (n.id === nodeId ? 'bold' : 'normal') : 'normal', fontSize: n.id === nodeId ? 14 : 12 },
                    zlevel: isHigh ? 1 : 0
                });
            });

            var newLinks = formattedLinks.map(function(l) {
                var isHigh = (l.source === nodeId || l.target === nodeId);
                return Object.assign({}, l, {
                    lineStyle: { color: isHigh ? (l.source === nodeId ? defaultNodeStyle.category0 : defaultNodeStyle.category1) : greyLine, opacity: isHigh ? 0.9 : 0.1, width: isHigh ? 2 : 1, curveness: 0.15 }
                });
            });

            myChart.setOption({ series: [{ data: newNodes, links: newLinks }] });
        }

        function resetGraph() {
            document.getElementById('searchInput').value = '';
            if (!isHighlighted) return;
            isHighlighted = false;
            myChart.setOption({ series: [{ data: formattedNodes, links: formattedLinks }] });
        }

        function searchNode() {
            var query = document.getElementById('searchInput').value.trim().toLowerCase();
            if (!query) { resetGraph(); return; }
            var foundNode = nodes.find(function(n) { return n.name.toLowerCase().indexOf(query) !== -1; });
            if (foundNode) { highlightNodeAndNeighbors(foundNode.id); } else { alert('未找到包含该名称的机构或公司'); }
        }
        
        document.getElementById('searchInput').addEventListener('keyup', function(event) { if (event.key === 'Enter') searchNode(); });
        myChart.on('click', function (params) { if (params.dataType === 'node') highlightNodeAndNeighbors(params.data.id); });
        myChart.getZr().on('click', function(event) { if (!event.target) resetGraph(); });
        window.addEventListener('resize', function() { myChart.resize(); });
    </script>
</body>
</html>
"""

final_html = html_template.replace('__DATA_JSON__', data_json)

os.makedirs("public", exist_ok=True)
out_file = "public/index.html"
with open(out_file, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Graph generated at: {out_file}")
