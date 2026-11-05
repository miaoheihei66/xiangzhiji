# 相纸机

## 目标
单文件网页应用 `index.html`：用手机摄像头实时取景，套上拍立得相纸边框和胶片色调，拍完存到相册。
发布在 GitHub Pages（必须 https，否则 iPhone 不给摄像头权限），用户在 iPhone Safari 打开并“添加到主屏幕”。

## 发布
- 网址：https://miaoheihei66.github.io/xiangzhiji/ （国内不开代理也能打开）
- 仓库：https://github.com/miaoheihei66/xiangzhiji （公开），main 分支根目录直接作为 Pages 站点。
- gh 是免安装版，在 `%LOCALAPPDATA%\gh-cli\bin\gh.exe`（已加进用户 PATH，已登录 miaoheihei66）。
- 电脑代理端口 7897，git 全局已设 http.proxy；gh 需要 `$env:HTTPS_PROXY="http://127.0.0.1:7897"`。winget 不走代理，从 GitHub 下东西会失败。
- 改完 `index.html` 后：`git add index.html; git commit -m "说明"; git push`，一两分钟后网页自动更新。
- 手机上看不到更新时，多半是缓存：从主屏幕图标完全关掉再开，或在 Safari 里刷新。
- 用户在中国大陆，推送失败先重试，再考虑代理（`git config --global http.proxy http://127.0.0.1:端口`）。

## 代码结构（都在 index.html）
- `FORMATS`：六种相纸尺寸（毫米），来自官方规格。Spectra 103 × 101 mm，画面 90 × 73 mm。
- `FILMS`：色调参数（polaroid、instax，spectra 由 polaroid 派生）。颜色部分不是拍脑袋定的：2026-11 从 Flickr 下了约 60 张宝丽来、70 张 Instax 真实扫描片和 42 张手机照片，测量黑白位、暗中亮部偏色、饱和度、红绿蓝色相，再拟合参数让手机照片经过滤镜后统计值对上真片。蓝色饱和度拟合值偏大（蓝衣服发紫），手动降到 0.25 和 0.30。
- 重新校色：`tools\` 里有脚本。fetch.py 下样本，measure.py 测统计（写 stats.json），fit.py 拟合（Python 版滤镜和着色器同一套算法，改着色器要同步改 fit.py 的 apply），preview.py 出对比图。fit 很慢，用环境变量 RES=48 PIT=2 NIT=600 加速。
- 实测结论：宝丽来黑位高且偏青、白位压暗偏暖、饱和度约手机七成；Instax 暗部偏红棕、亮部偏冷、对比更强、饱和度约手机八成。两者红色都偏洋红、蓝色偏紫。
- `FRAMES`：11 种边框颜色；`paintFrame()` 同时画取景预览和成品（纸纹、柔光、切边高光、画面窗口凹陷）。深色边框时桌面背景自动变浅。
- 镜头：`classify()` 靠摄像头名字（超广角、长焦、前置等）判断 0.5×、1×、长焦，取景框下方可切换。
- 片段着色器 `FS`：WebGL 胶片效果，取景和拍照共用。
- `shoot()`：按 14 像素每毫米输出整张相纸，每次快门随机偏一点色温和曝光。
- 保存：优先 `navigator.share` 调起 iOS 分享菜单，否则提示长按保存。`window.claude` 分支是给 claude.ai 用的，保留即可。

## 已知问题（用户没要求先别改）
- 手写字体（Long Cang、Zhi Mang Xing）从 Google Fonts 加载，国内常加载不到。可改成把字体文件放进仓库自己加载。
- 色调按资料调的，还没用真实照片校对，等用户试拍反馈。

## 沟通习惯
- 全程中文，少中英混排；回复里不要出现斜杠符号（命令、路径、网址除外）。
