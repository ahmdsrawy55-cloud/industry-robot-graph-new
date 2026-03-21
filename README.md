# 投资网络生成器

这个项目用于自动生成“投资网络拓扑图”。

## 如何使用

只要当你需要更新数据时：
1. 用新的 Excel 文件替换 `data/data.xlsx`（请保持列名 `Source` 和 `Target` 不变）。
2. `git commit` 并 `git push` 到 GitHub 的主干分支 (main)。
3. GitHub Actions 会自动在后台运行 Python 脚本生成新的网页，并推送到 GitHub Pages 上。

## 本地预览

如果想在本地生成网页：
```bash
pip install -r requirements.txt
python build_graph.py
```
生成的网页会出现在 `public/index.html`。
双击即可在浏览器中查看。
