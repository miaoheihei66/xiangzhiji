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
- `FILMS`：三套色调参数（spectra、polaroid、instax）。用户说“太艳、太灰、偏色不对”就改这里。
- 片段着色器 `FS`：WebGL 胶片效果，取景和拍照共用。
- `shoot()`：按 14 像素每毫米输出整张相纸，每次快门随机偏一点色温和曝光。
- 保存：优先 `navigator.share` 调起 iOS 分享菜单，否则提示长按保存。`window.claude` 分支是给 claude.ai 用的，保留即可。

## 已知问题（用户没要求先别改）
- 手写字体（Long Cang、Zhi Mang Xing）从 Google Fonts 加载，国内常加载不到。可改成把字体文件放进仓库自己加载。
- 色调按资料调的，还没用真实照片校对，等用户试拍反馈。

## 沟通习惯
- 全程中文，少中英混排；回复里不要出现斜杠符号（命令、路径、网址除外）。
