# Agent Skills

[中文](README.md) | [English](README.en.md)

一组给 AI 编程助手（DSH、Claude Code 等）用的**技能包**：每个技能解决一类重复劳动，装上就能按名调用。

## 收录

| 技能 | 用途 | 目录 |
| --- | --- | --- |
| `kaoyan-phrases` | 从英文材料里提取考研英语固定搭配，累计进 Excel 总表，交付 Anki CSV 与 Word 讲义 | [`skills/kaoyan-phrases`](skills/kaoyan-phrases) |

## 安装

技能就是「一个文件夹 + 一个 `SKILL.md`」。把对应目录复制到助手的技能目录即可，无需重启：

```powershell
# DSH
Copy-Item skills\kaoyan-phrases "$HOME\.dsh\skills\" -Recurse

# Claude Code
Copy-Item skills\kaoyan-phrases "$HOME\.claude\skills\" -Recurse
```

装好后在对话里直接说需求就会触发，例如「把这篇阅读里的固定搭配整理成词组表」。

## 目录约定

```
skills/<技能名>/
├── SKILL.md          入口：什么时候用、怎么用、硬规则（带 YAML frontmatter）
├── README.md         给人看的说明：用途、用法、产出、安装
├── references/       分步细化的说明，SKILL.md 里按步引用
├── tools/            可执行脚本
├── examples/         示例输入与产出
└── LICENSE
```

- `SKILL.md` 的 `description` 决定**何时触发**，写清楚「做什么 + 什么场景用」。
- 正文只在技能被使用时加载，所以细节可以放在 `references/` 里，主文件保持短。
- 脚本用相对当前工作目录的路径，产出落到用户自己的项目里，不写死盘符。

## 贡献

欢迎提 Issue 或 PR：新技能按上面的目录约定放好，并在根 README 的表格里登记一行。

## License

MIT，见 [LICENSE](LICENSE)。
