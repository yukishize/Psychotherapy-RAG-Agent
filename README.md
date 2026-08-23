# 心理治疗 Agent（RAG）

基于 RAG 的心理治疗助手：通过**不经过 LLM 的问卷引擎**获取用户初步评估，再结合知识库（自愈治疗方法 + agent 话术/敏感点 + 询问方向）驱动对话生成。

> 本项目仅提供自愈方法与陪伴式对话，**不替代专业诊断与治疗**。raw/ 目录中的原始文件不在本框架范围内，可忽略。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 目录结构

```
├── main.py                  # CLI 入口（问卷 → 评估 → 聊天）
├── config.yaml              # LLM 与路径配置
├── .env.example             # API key 示例
├── qengine/                 # 问卷引擎（纯规则计分，不经过 LLM）
│   ├── parser.py            #   解析 YAML frontmatter + markdown 题目表
│   ├── scorer.py            #   维度计分 / 反向计分 / 转换 / 关键项 / 测谎项
│   ├── cli_flow.py          #   终端交互答题
│   └── registry.py          #   问卷加载
├── questionaire/            # 问卷数据（md），含评测标准，框架据此自动计分
├── rag/                     # 轻量自建 RAG
│   ├── loader.py            #   知识库 md → 分块文档
│   ├── store.py             #   numpy 向量库 + index.json/npz 持久化
│   ├── retriever.py         #   元数据过滤（tags/severity）+ 余弦检索
│   ├── embeddings.py        #   OpenAI 兼容 embedding 客户端
│   ├── build_index.py       #   索引构建命令
│   └── knowledge/           # 知识库（待补充数据）
│       ├── treatment/       #   自愈治疗方法（给用户看）
│       └── scripts/         #   agent 话术 / 敏感点 / 询问方向（注入提示词）
├── agent/                   # 对话层
│   ├── llm.py               #   OpenAI 兼容聊天客户端
│   ├── prompts.py           #   系统提示词构造 + 危机文本
│   └── session.py           #   会话状态机 + 安全护栏
└── tests/                   # pytest 单元测试
```

## 安装

```bash
pip install -r requirements.txt
copy .env.example .env        # 填入 API key
```

在 `config.yaml`（或 `.env`）中配置 OpenAI 兼容服务。聊天与 embedding 可各自独立：

```yaml
llm:
  chat:
    base_url: https://api.deepseek.com   # 或 OpenAI 等
    api_key_env: OPENAI_API_KEY
    model: deepseek-v4-flash
  embedding:
    base_url: https://api.siliconflow.cn/v1   # 需提供 OpenAI 兼容 embeddings 接口
    api_key_env: EMBEDDING_API_KEY
    model: BAAI/bge-m3
```

> 说明：DeepSeek 不提供 embedding 接口，embedding 需另配支持 `/embeddings` 的服务（硅基流动/智谱/通义/OpenAI 等）；`llm.embedding` 未配置时，RAG 自动降级为关键词/元数据过滤。

## 使用

```bash
# 1. 构建 RAG 索引（需先填充 rag/knowledge/ 下的文档）
py -3 -m rag.build_index

# 2. 启动
py -3 main.py
```

聊天中命令：`/quiz` 重新评估、`/help` 帮助、`/quit` 退出。

## 问卷引擎（不经过 LLM）

`questionaire/*.md` 的 YAML frontmatter 即评测标准：

- `dimensions`：维度与包含的题号（支持 `items: "1-90"` 范围，因子维度用 `value_type: mean`）
- `scoring`：各维度的 `[低, 高]` 区间 → 等级与建议
- 特殊元数据：`scoring_transform`（SAS 标准分 ×1.25）、`scoring_method: percent`（SDS 严重度指数）、`critical_item`（PHQ-9 项目9 自伤关键项 >1 触发风险）、`lie_item`（测谎题）、`additional_items`（SCL-90 附加题仅计入总分）、`total_positive_threshold`
- 反向计分直接读取题目表格的「反向计分」列

评估结果（JSON 评估档案）用于：① 向用户展示等级与建议；② 生成 RAG 检索标签（如 `depression + moderate`）；③ 注入 agent 系统提示词。

## 知识库格式

每个 md 文件带 frontmatter（详见 `rag/knowledge/*/_template.md`）：

```yaml
---
id: cbt_basics
category: treatment      # treatment（给用户）/ script（给 agent）
target: user             # user / agent
tags: [depression, anxiety]   # 心理维度关键词，用于过滤
severity: [mild, moderate]    # 适用严重度，避免误推
---
```

正文按 `##` 分块，每个分块作为一个检索单元。当前为 MD 唯一格式；loader 采用「元数据提取 + 正文分块」接口，后续新增格式只需扩展 reader。

## 安全护栏

问卷命中自伤关键项（如 PHQ-9 项目9 >1）时：结果页直接显示危机提示（含 12356 心理援助热线）；对话层注入安全优先指令，要求先共情、提供热线与就医建议，**不推荐自愈方法**。

## 测试

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 py -3 -m pytest tests -q
```

## 免责声明

本项目输出的内容仅供参考与自助陪伴，不构成医疗建议。出现自伤、自杀风险时请立即联系专业机构或拨打急救电话。

## License

本项目代码以 [MIT License](LICENSE) 开源。

**NOTICE（问卷版权）**：`questionaire/` 中的量表内容版权归各自原作者及发行商所有：
- PHQ-9、GAD-7：公共领域；
- SCL-90（Derogatis）、SAS/SDS（Zung）等为受版权保护的商业量表，本仓库对其仅作学习参考，**不授予使用授权**；商用或分发前请自行核实并取得相应授权。

以上版权声明不随 MIT 许可一并转移。
