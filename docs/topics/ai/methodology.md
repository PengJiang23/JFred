---
title: 07 · 调研方法与插图许可
description: AI 系统学习指南 · 07 · 调研方法与插图许可
topic: AI 学习
sourceDate: 2026-10-05
---

# 07 · 调研方法与插图许可

[专栏导读](./) · [参考资料](./references) · [来源与许可](./methodology)

> 整理自《从原理到业务的 AI 系统学习指南》，调研截止 2026 年 10 月 5 日。研究结论保留原有条件与来源；时效信息请结合原文日期阅读。

阅读版将知识地图、流程图、公式和参考资料集中在同一文档中；HTML支持目录过滤和浏览器全文查找，PDF适合保存与批注，Markdown保留可编辑正文。引用台账记录论文标识、主题、核心发现、局限与实际核验范围，BibTeX方便后续文献管理。评测模板中的数据和阈值为教学示例，应先按真实业务修改。

后续更新时，优先刷新前沿与工程文档的版本，再用自己的业务测试集检查适用性；基础概念通常较稳定，模型价格、API行为、仓库接口和排行榜则需要重新核验。保留旧版本及变更原因，避免把资料更新误当作系统能力已经提升。


## 如何读证据而不被数字误导

本文采用四种证据表述。**“论文实验/研究结果”**指来源给出了数据、方法或实验；它只支持对应任务、样本和设置内的结论。**“作者/项目方报告”**包括官方技术报告、博客和仓库说明，能解释系统设计或复现入口，但不是独立审计。**“探索性结果”**表示方法仍受小样本、受控环境或泛化未知的限制。**“调研归纳/工程建议”**是将多个来源转化成开发决策，需在你的数据上验证。

“有论文”与“结论已充分确立”不同。预印本可以包含很有价值的开放实验，正式发表的论文也可能只有窄范围证据。看成果时应同时询问：测了什么任务、比较了什么基线、计算预算是否相同、用了多少次尝试、谁负责评分、有没有失败样本、能不能重做。单次成功视频、挑选的示例、GitHub 星数与参数量都不能替代这些信息。

下列区别贯穿全文：**正确性**是答案或动作是否符合任务事实；**忠实性/有据性**是输出是否得到给定证据支持；**有用性**是能否帮助用户完成任务。错误文档被准确复述，可以很忠实却不正确；正确但缺少关键步骤的答案，可能仍然无用。对同一个模型，更换上下文、工具、提示、采样预算和执行环境，端到端表现也会改变。

## 调研方法和边界

本次采用**有来源台账的主题型叙述综述**，不是声称穷尽所有研究的系统综述，也不把不同论文结果合并为元分析。并行检索围绕机制、应用和评测问题展开，基础部分保留经典文献，前沿部分额外检索近期研究及后续修订。检索入口包括学术搜索、arXiv、正式会议与出版平台，以及作者机构的文档、仓库和工程材料。具体命中及阅读范围保存在随文引用台账中；不虚构全网检索总量或 PRISMA 筛选数字。

论文以 arXiv 主编号、DOI 和规范化题名交叉去重。同一研究的预印本、会议版本和修订版本仅计一篇，博客、课程、仓库不计入论文数量。参考文献年份按引用版本标注：arXiv 条目主要记录首次公开年份，明确引用期刊版的条目使用期刊发表年份；时效讨论区分首次提出与后续修订，不把修订年份当作全新研究。**核验含义是确认研究真实存在、标识和题名相符，并检查支持正文结论的原始资料；不意味着独立复现了实验。** 阅读范围逐项记录：部分研究精读方法和实验，其他条目主要依据原始摘要与项目说明，不把摘要阅读冒充全文精读。

截止日期是本次资料核验的时间边界，不意味着覆盖截至该日的全部研究，也不意味着所有链接永远保持原样。本文不推断未公开的模型权重、训练数据、私有业务架构、成本或线上指标。生成式 AI 之外，传统机器学习、推荐、运筹优化、计算机视觉、机器人与因果推断各自仍是广阔领域；本文会交代关系，但不将它们压缩成“大模型的子领域”。

文中的示意架构、知识地图、类比和建议性验收阈值，均是为教学组织的归纳。出现“示例”“建议”“假设”时，不应理解为某厂商真实部署数据。视频材料仅在确实核验到章节时间信息时提供时间点，其余给出官方章节定位与实际阅读依据。


## 插图来源与使用说明

本版将原论文图、官方项目图和原创教学图穿插在对应主题中。第三方图片保持原图，中文解读另行撰写；图片原始地址、署名与许可依据记录在《插图来源与许可.json》。不同图片适用各自的许可，不能把整本指南的分享方式推定为每张图片的许可。

- **图 01｜AI 系统的四层知识地图**。本指南原创教学图。本图采用 CC BY 4.0；第三方图像不受此声明覆盖。
- **图 02｜从问题到证据再到验收**。本指南原创教学图。本图采用 CC BY 4.0；第三方图像不受此声明覆盖。
- **图 03｜推理预算在顺序修订与并行采样间的分配**。[Charlie Snell, Jaehoon Lee, Kelvin Xu, Aviral Kumar (2024), Figure 7](https://arxiv.org/html/2408.03314v1#S6.F7)。CC BY 4.0。
- **图 04｜DeepSeek-R1 的多阶段训练流程**。[Daya Guo et al. / DeepSeek-AI (2025), Nature, Figure 2](https://www.nature.com/articles/s41586-025-09422-z#Fig2)。CC BY 4.0。
- **图 05｜视频生成的时空表示与条件信息流**。[本学习文档原创绘图；机制依据 LDM、DiT 与 Wan](https://arxiv.org/abs/2503.20314)。原创示意图（无第三方图形复制）。
- **图 06｜ReAct 如何利用环境观察修订行动**。[Shunyu Yao et al. (2022/2023), ReAct, Figure 1](https://arxiv.org/html/2210.03629v3#S1.F1)。CC BY 4.0。
- **图 07｜SimpleMem 的写入、整合与检索**。[Copyright (c) 2025 AIMING Lab](https://github.com/aiming-lab/SimpleMem/blob/db80b6a7c591e0ea730a058e9f5fc4eb06572299/fig/Fig_framework.png)。MIT。
- **图 08｜MoE 与 MLA 优化不同资源**。[本学习文档原创绘图；机制依据 DeepSeek-V3](https://arxiv.org/abs/2412.19437)。原创示意图（无第三方图形复制）。
- **图 09｜Kimi Linear 的 KDA、MLA 与 MoE 混合结构**。[Copyright (c) 2025 Moonshot AI](https://github.com/MoonshotAI/Kimi-Linear/blob/8c1d85eb6b5f8fcefb15758691b0ce50b0827ce3/figures/arch.png)。MIT。
- **图 10｜从预测周围词学习词向量**。[Aston Zhang、Zachary C. Lipton、Mu Li、Alexander J. Smola 与 D2L 贡献者；Copyright 2019 Amazon.com, Inc. or its affiliates](https://d2l.ai/chapter_natural-language-processing-pretraining/word2vec.html)。CC BY-SA 4.0（教材文档及图；未采用仅适用于示例代码的 MIT 许可）。
- **图 11｜查询、键、值与加权汇总**。[Aston Zhang、Zachary C. Lipton、Mu Li、Alexander J. Smola 与 D2L 贡献者；Copyright 2019 Amazon.com, Inc. or its affiliates](https://d2l.ai/chapter_attention-mechanisms-and-transformers/queries-keys-values.html)。CC BY-SA 4.0（教材文档及图）。
- **图 12｜把注意力放回 Transformer 的整体结构**。[Aston Zhang、Zachary C. Lipton、Mu Li、Alexander J. Smola 与 D2L 贡献者；Copyright 2019 Amazon.com, Inc. or its affiliates](https://d2l.ai/chapter_attention-mechanisms-and-transformers/transformer.html)。CC BY-SA 4.0（教材文档及图）。
- **图 13｜潜空间扩散的训练与生成路径**。[本学习文档原创中文机制图；依据 Rombach 等人的 LDM 研究](https://arxiv.org/abs/2112.10752)。原创示意图（无第三方图形复制）。
- **图 14｜全量微调、LoRA 与 QLoRA 的内存来自哪里**。[Tim Dettmers、Artidoro Pagnoni、Ari Holtzman、Luke Zettlemoyer，QLoRA（2023）](https://arxiv.org/abs/2305.14314)。CC BY 4.0（已核验 arXiv 摘要页 Rights 链接；保留原 Figure 1 与英文图题）。
- **图 15｜真实服务中的 KV 缓存按层类型与物理块管理**。[vLLM 项目贡献者，Hybrid KV Cache Manager 设计文档](https://docs.vllm.ai/en/latest/design/hybrid_kv_cache_manager/)。Apache-2.0（官方仓库文档资源，已保留完整 LICENSE；图片未改）。
- **图 16｜GraphRAG：离线图索引与在线全局回答**。[Darren Edge 等，From Local to Global，Figure 1](https://arxiv.org/html/2404.16130v2#S3.F1)。CC BY 4.0。
- **图 17｜SWE-agent：模型之外还有环境、工具和历史处理**。[SWE-agent 项目，John Yang、Carlos E. Jimenez、Alexander Wettig、Shunyu Yao、Karthik Narasimhan、Ofir Press 等贡献者](https://swe-agent.com/latest/background/architecture/)。MIT。
- **图 18｜Docling：不同文件先汇入统一文档对象**。[The Docling Contributors](https://docling-project.github.io/docling/concepts/architecture/)。MIT。
- **图 19｜τ-bench：对话、规则与数据库状态要一起测**。[Shunyu Yao、Noah Shinn、Pedram Razavi、Karthik Narasimhan，τ-bench，Figure 1](https://arxiv.org/html/2406.12045v1#S1.F1)。CC BY 4.0。
- **图 20｜ComfyUI：看懂一个文生图工作流的数据依赖**。[Comfy-Org docs contributors，Text to Image Workflow 官方教程配图](https://docs.comfy.org/tutorials/basic/text-to-image)。GPL-3.0（所引文档仓库许可；图片作为独立原始作品随文提供）。
- **图 21｜同一组试验，pass@k与pass^k会走向不同方向**。[Shunyu Yao、Noah Shinn、Pedram Razavi、Karthik Narasimhan，τ-bench，Figure 4](https://arxiv.org/html/2406.12045v1#S5.F4)。CC BY 4.0。
- **图 22｜以产物为节点的学习路线**。本指南原创教学图。本图采用 CC BY 4.0；第三方图像不受此声明覆盖。
- **图 23｜把错误症状路由到可检查的证据**。本指南原创教学图。本图采用 CC BY 4.0；第三方图像不受此声明覆盖。
