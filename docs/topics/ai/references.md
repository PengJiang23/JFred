---
title: 06 · 参考资料与论文索引
description: AI 系统学习指南 · 06 · 参考资料与论文索引
topic: AI 学习
sourceDate: 2026-10-05
---

# 06 · 参考资料与论文索引

[专栏导读](./) · [参考资料](./references) · [来源与许可](./methodology)

> 整理自《从原理到业务的 AI 系统学习指南》，调研截止 2026 年 10 月 5 日。研究结论保留原有条件与来源；时效信息请结合原文日期阅读。

正文实际引用、按研究主标识去重后共 **98 篇论文**。原始记录 107 条，合并跨板块重复 9 条。期刊版与预印本只计一次；下列编号全篇通用，点击题名或正文编号可打开原始来源。作者过多的条目在正文列首三位，完整作者与核验范围见随附引用台账。

## 前沿与能力发展

**P001**　DeepSeek-AI; Guo, Daya; Yang, Dejian 等（2025）。[DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948)。arXiv:2501.12948。主题：推理与后训练。

阅读要点：可验证奖励强化学习、冷启动与多阶段后训练，及大到小推理蒸馏。 边界：主结果受基座、可验证任务、采样配置与版本影响；R1-Zero不等于无数据训练。

**P002**　Snell, Charlie; Lee, Jaehoon; Xu, Kelvin 等（2024）。[Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters](https://arxiv.org/abs/2408.03314)。arXiv:2408.03314。主题：推理时计算。

阅读要点：按难度选择搜索或修订，可比固定best-of-N更有效分配计算。 边界：小模型超过大模型的结果有FLOPs匹配与小模型本已有非零成功率等条件。

**P003**　Muennighoff, Niklas; Yang, Zitong; Shi, Weijia 等（2025）。[s1: Simple test-time scaling](https://arxiv.org/abs/2501.19393)。arXiv:2501.19393。主题：推理时计算。

阅读要点：精选1000条推理数据SFT与budget forcing，展示推理长度控制。 边界：强基座、教师轨迹与预算不可从成本讨论中剔除；竞赛数学结果不等于通用能力。

**P004**　Yang, An; Li, Anfeng; Yang, Baosong 等（2025）。[Qwen3 Technical Report](https://arxiv.org/abs/2505.09388)。arXiv:2505.09388。主题：推理与模型技术报告。

阅读要点：统一思考/非思考模式、思考预算、稠密与MoE模型系列。 边界：技术报告自述，基准表现需在业务语言、领域与约束上复测。

**P005**　Zhao, James Xu; Hooi, Bryan; Ng, See-Kiong（2025）。[Test-Time Scaling in Reasoning Models Is Not Effective for Knowledge-Intensive Tasks Yet](https://arxiv.org/abs/2509.06861)。arXiv:2509.06861。主题：推理与事实性。

阅读要点：额外闭卷推理计算不稳定改善知识密集任务，回答倾向会改变幻觉率。 边界：研究是特定模型与知识基准，并非证明所有推理计算无效。

**P006**　Bilal, Ahsan; Mohsin, Muhammad Ahmed; Umer, Muhammad 等（2026）。[Refining Over Resampling: Test-Time Self-Correction for LLM Reasoning](https://arxiv.org/abs/2608.05643)。arXiv:2608.05643。主题：2026推理时计算探索。

阅读要点：多候选加候选内修订再聚合，对数学基准报告提升。 边界：开放式事实任务的泛化未由这些数学实验建立；自我检查并非独立验证。

**P007**　Radford, Alec; Kim, Jong Wook; Hallacy, Chris 等（2021）。[Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020)。arXiv:2103.00020。主题：多模态表示。

阅读要点：图文对比学习提供可迁移视觉表示和零样本接口。 边界：语义匹配不等于图像生成、可靠OCR或像素测量。

**P008**　Liu, Haotian; Li, Chunyuan; Wu, Qingyang 等（2023）。[Visual Instruction Tuning](https://arxiv.org/abs/2304.08485)。arXiv:2304.08485。主题：多模态理解。

阅读要点：连接视觉编码器与LLM，并用视觉指令数据训练对话。 边界：早期合成指令评测与实际文档场景不同，无法代表当前产品排名。

**P009**　Bai, Shuai; Chen, Keqin; Liu, Xuejing 等（2025）。[Qwen2.5-VL Technical Report](https://arxiv.org/abs/2502.13923)。arXiv:2502.13923。主题：2025视觉理解。

阅读要点：动态分辨率、绝对时间表示、目标定位与文档/视频理解。 边界：技术报告及特定评测；真实扫描质量、业务规则和长尾样式需另测。

**P010**　Ho, Jonathan; Jain, Ajay; Abbeel, Pieter（2020）。[Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239)。arXiv:2006.11239。主题：图像生成基础。

阅读要点：学习去噪过程实现高质量生成。 边界：图像分布指标不保证提示遵循或业务正确性。

**P011**　Rombach, Robin; Blattmann, Andreas; Lorenz, Dominik 等（2021）。[High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752)。arXiv:2112.10752。主题：潜空间图像生成。

阅读要点：在预训练自编码器潜空间扩散，降低高分辨率生成成本。 边界：压缩带来信息取舍；不能保证每个细节被条件精确控制。

**P012**　Peebles, William; Xie, Saining（2022）。[Scalable Diffusion Models with Transformers](https://arxiv.org/abs/2212.09748)。arXiv:2212.09748。主题：扩散网络架构。

阅读要点：用Transformer处理潜空间图块，研究算量规模与生成质量。 边界：ImageNet条件生成等实验与开放式产品需求不同。

**P013**　Liu, Xingchao; Gong, Chengyue; Liu, Qiang（2022）。[Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow](https://arxiv.org/abs/2209.03003)。arXiv:2209.03003。主题：流生成模型。

阅读要点：学习连接分布的较直ODE轨迹，提高少步生成的可能性。 边界：数学路径与特定实验不能保证所有任务一步生成无质量损失。

**P014**　Wan, Team; Wang, Ang; Ai, Baole 等（2025）。[Wan: Open and Advanced Large-Scale Video Generative Models](https://arxiv.org/abs/2503.20314)。arXiv:2503.20314。主题：2025视频生成。

阅读要点：开放视频VAE、扩散Transformer及多种视频任务。 边界：论文自述比较并非通用商业质量结论；资源取决于时长分辨率。

**P015**　Xu, Jin; Guo, Zhifang; He, Jinzheng 等（2025）。[Qwen2.5-Omni Technical Report](https://arxiv.org/abs/2503.20215)。arXiv:2503.20215。主题：2025全模态音频交互。

阅读要点：Thinker–Talker协调感知、文字与流式语音，并对齐音视频。 边界：端到端并不消除模块、同步和交互轮次等系统问题。

**P016**　Radford, Alec; Kim, Jong Wook; Xu, Tao 等（2022）。[Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356)。arXiv:2212.04356。主题：语音识别。

阅读要点：大规模弱监督多语言多任务训练改善跨数据集泛化。 边界：识别模型不等于完整实时对话系统，噪声专业名词需另测。

**P017**　Yao, Shunyu; Zhao, Jeffrey; Yu, Dian 等（2022）。[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)。arXiv:2210.03629。主题：Agent行动循环。

阅读要点：交替推理与行动，利用外部观察修订任务进程。 边界：原始基准和模型设定有限；工具调用的可靠性需系统验收。

**P018**　Schick, Timo; Dwivedi-Yu, Jane; Dessì, Roberto 等（2023）。[Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)。arXiv:2302.04761。主题：工具调用训练。

阅读要点：自监督学习何时调用API、参数及结果的利用。 边界：API集合与训练方式不等于任意业务工具授权或执行可靠性。

**P019**　Wang, Guanzhi; Xie, Yuqi; Jiang, Yunfan 等（2023）。[Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291)。arXiv:2305.16291。主题：Agent技能与记忆。

阅读要点：自动课程、代码技能库、环境反馈循环形成可复用能力。 边界：Minecraft环境；外部技能学习不同于模型权重在线更新。

**P020**　Yang, John; Jimenez, Carlos E.; Wettig, Alexander 等（2024）。[SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793)。arXiv:2405.15793。主题：代码Agent接口。

阅读要点：专门的Agent-computer interface改善仓库导航编辑执行行为。 边界：2024历史模型/基准分数不代表2026上限；测试并非全部工程需求。

**P021**　Yao, Shunyu; Shinn, Noah; Razavi, Pedram 等（2024）。[$\tau$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045)。arXiv:2406.12045。主题：Agent端到端评测。

阅读要点：用户交互、政策规则和最终数据库状态验收；重复运行可靠性。 边界：用户模拟和受控领域并不覆盖所有真实客服复杂性。

**P022**　Liu, Nelson F.; Lin, Kevin; Hewitt, John 等（2023）。[Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)。arXiv:2307.03172。主题：长上下文有效利用。

阅读要点：证据位置影响多文档问答和键值检索表现。 边界：历史模型的下降幅度不能直接套用当前模型。

**P023**　Hsieh, Cheng-Ping; Sun, Simeng; Kriman, Samuel 等（2024）。[RULER: What's the Real Context Size of Your Long-Context Language Models?](https://arxiv.org/abs/2404.06654)。arXiv:2404.06654。主题：长上下文评测。

阅读要点：多针、多跳和聚合比单针检索更全面衡量有效上下文。 边界：合成评测仍不等于完整业务文档推理。

**P024**　Asai, Akari; Wu, Zeqiu; Wang, Yizhong 等（2023）。[Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511)。arXiv:2310.11511。主题：自适应RAG。

阅读要点：训练反思标记控制检索、生成及证据评价。 边界：用普通提示词反思不等于复现论文训练方法。

**P025**　Packer, Charles; Wooders, Sarah; Lin, Kevin 等（2023）。[MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)。arXiv:2310.08560。主题：外部记忆管理。

阅读要点：借鉴操作系统分层存储，管理有限上下文与持久记录。 边界：语义搬运并非无损字节复制，记忆写入可能出错。

**P026**　Liu, Jiaqi; Su, Yaofeng; Xia, Peng 等（2026）。[SimpleMem: Efficient Lifelong Memory for LLM Agents](https://arxiv.org/abs/2601.02553)。arXiv:2601.02553。主题：2026应用记忆。

阅读要点：结构化压缩、整合与按查询检索，LoCoMo上改善效果与token指标。 边界：本文数字固定到v1；摘要称lossless并非任意经历的无损保证；表中token不等于总账单。

**P027**　Behrouz, Ali; Zhong, Peilin; Mirrokni, Vahab（2024）。[Titans: Learning to Memorize at Test Time](https://arxiv.org/abs/2501.00663)。arXiv:2501.00663。主题：神经记忆探索。

阅读要点：测试时学习神经长期记忆并与注意力结合。 边界：内部状态不等于可审计可删除的应用数据库记忆。

**P028**　Rajib, Rakibul Hasan; Zheng, Mengxin; Lou, Qian（2026）。[Learning What to Retain: Gated-Memory Routing for Efficient Collaboration in Multi-Agent LLM Systems](https://arxiv.org/abs/2609.00237)。arXiv:2609.00237。主题：2026多Agent记忆路由。

阅读要点：学习写入、检索门与停止控制，减少不必要执行历史。 边界：可验证封闭域任务；参数成本代理不完整覆盖墙钟延迟/显存/批处理。

**P029**　Gu, Albert; Dao, Tri（2023）。[Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752)。arXiv:2312.00752。主题：状态空间架构。

阅读要点：输入相关选择性状态和硬件算法实现长序列建模。 边界：有限状态压缩和小中规模比较限制跨规模结论。

**P030**　Dao, Tri; Gu, Albert（2024）。[Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality](https://arxiv.org/abs/2405.21060)。arXiv:2405.21060。主题：状态空间架构。

阅读要点：SSM与注意力的结构化对偶关系支持更快核心层。 边界：内核加速倍数不是端到端任意负载加速。

**P031**　DeepSeek-AI; Liu, Aixin; Feng, Bei 等（2024）。[DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437)。arXiv:2412.19437。主题：MoE与模型效率。

阅读要点：组合MoE、MLA、均衡和多token训练等工程设计。 边界：激活参数不等于总显存；报告训练费用不等于全部研发成本。

**P032**　Penedo, Guilherme; Kydlíček, Hynek; allal, Loubna Ben 等（2024）。[The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale](https://arxiv.org/abs/2406.17557)。arXiv:2406.17557。主题：预训练数据。

阅读要点：公开去重过滤与教育质量筛选消融。 边界：数据质量依赖目标，过滤可能损害长尾语言和领域覆盖。

**P033**　Gunasekar, Suriya; Zhang, Yi; Aneja, Jyoti 等（2023）。[Textbooks Are All You Need](https://arxiv.org/abs/2306.11644)。arXiv:2306.11644。主题：高质量合成数据。

阅读要点：教材风格与合成练习改善小型代码模型。 边界：不能外推为所有合成数据均有益，教师能力与验证条件重要。

**P034**　Shumailov, Ilia; Shumaylov, Zakhar; Zhao, Yiren 等（2023）。[The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493)。arXiv:2305.17493。主题：合成数据风险。

阅读要点：递归生成数据训练可损失原始分布尾部。 边界：不等于有验证且保留真实数据的所有合成数据策略必然崩溃。

**P035**　Wallace, Eric; Xiao, Kai; Leike, Reimar 等（2024）。[The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions](https://arxiv.org/abs/2404.13208)。arXiv:2404.13208。主题：提示注入与模型安全。

阅读要点：通过训练区分指令优先级，提高冲突指令鲁棒性。 边界：不等于防御全部注入，不替代工具权限和服务端鉴权。

**P036**　Turpin, Miles; Michael, Julian; Perez, Ethan 等（2023）。[Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting](https://arxiv.org/abs/2305.04388)。arXiv:2305.04388。主题：解释忠实性。

阅读要点：思维链可能未披露真正影响答案的提示偏置。 边界：实验模型较早，具体幅度不能直接用于新模型；仍需独立验证忠实性。

**P037**　Kimi Team; Zhang, Yu; Lin, Zongyu 等（2025）。[Kimi Linear: An Expressive, Efficient Attention Architecture](https://arxiv.org/abs/2510.26692)。arXiv:2510.26692。主题：2025混合注意力。

阅读要点：KDA与MLA混合在匹配训练中兼顾质量、KV容量与长序列速度。 边界：最高6倍为1M上下文特定解码设定，短上下文不同。

**P038**　Yeo, Woongyeong; Kim, Kangsan; Yoon, Jaehong 等（2025）。[WorldMM: Dynamic Multimodal Memory Agent for Long Video Reasoning](https://arxiv.org/abs/2512.02425)。arXiv:2512.02425。主题：多模态长期记忆。

阅读要点：事件、语义、视觉记忆与自适应多粒度检索用于长视频问答。 边界：不能据此认定任意长视频可无损摘要或稳定因果推理。

**P039**　Lim, Junghwan; Cheung, Wai Ting; Ha, Minsu 等（2026）。[Motif-Video 2B: Technical Report](https://arxiv.org/abs/2604.16503)。arXiv:2604.16503。主题：2026视频生成与评测。

阅读要点：分离文本控制/表示/细节，报告VBench与人工偏好不一致。 边界：40个提示人工研究样本小；部分技术组合不是严格独立因果消融。

**P040**　Sebastian Farquhar; Jannik Kossen; Lorenz Kuhn 等（2024）。[Detecting hallucinations in large language models using semantic entropy](https://www.nature.com/articles/s41586-024-07421-0)。DOI:10.1038/s41586-024-07421-0。主题：不确定性与幻觉。

阅读要点：按语义聚合样本，检测部分随生成不稳定出现的错误。 边界：稳定重复错误可能低熵，检测信号不是事实证明。

**P041**　Adam Tauman Kalai; Ofir Nachum; Santosh S. Vempala 等（2026）。[Evaluating large language models for accuracy incentivizes hallucinations](https://www.nature.com/articles/s41586-026-10549-w)。arXiv:2509.04664。主题：2026幻觉与评测激励。

阅读要点：准确率单一激励偏好猜测；公开评分规则与拒答激励改变评测。 边界：形式化结论有假设，案例非统一成本模型排名，与2025预印本去重。

## 原理 训练与推理工程

**P042**　Vaswani, Ashish; Shazeer, Noam; Parmar, Niki 等（2017）。[Attention Is All You Need](https://arxiv.org/abs/1706.03762)。arXiv:1706.03762。主题：模型架构。

阅读要点：提出以注意力为核心的 Transformer，在机器翻译等任务中验证并行计算与质量收益 边界：原始实验并非现代全部聊天场景；架构含前馈网络等组件，不能把能力归因于注意力单一模块

**P043**　Sennrich, Rico; Haddow, Barry; Birch, Alexandra（2015）。[Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909)。arXiv:1508.07909。主题：Token与分词。

阅读要点：将子词及 BPE 用于处理机器翻译罕见词和开放词表问题 边界：原始任务为翻译；不同分词器的语言和代码效率需实测

**P044**　Mikolov, Tomas; Chen, Kai; Corrado, Greg 等（2013）。[Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781)。arXiv:1301.3781。主题：Embedding。

阅读要点：用高效训练方法学习词的连续向量表示并评估语法和语义相似性 边界：静态词向量不等于上下文表示，也不等于现代文档检索向量

**P045**　Devlin, Jacob; Chang, Ming-Wei; Lee, Kenton 等（2018）。[BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805)。arXiv:1810.04805。主题：模型架构。

阅读要点：双向 Transformer 预训练可迁移至问答与语言理解任务 边界：以理解与表示为主，不能直接等同自回归聊天模型

**P046**　Brown, Tom B.; Mann, Benjamin; Ryder, Nick 等（2020）。[Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)。arXiv:2005.14165。主题：预训练与上下文学习。

阅读要点：在不更新梯度的前提下，通过任务说明与少样本示范进行多任务测试 边界：某些任务仍困难；网页训练造成污染等方法学问题

**P047**　Kaplan, Jared; McCandlish, Sam; Henighan, Tom 等（2020）。[Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361)。arXiv:2001.08361。主题：规模规律。

阅读要点：经验研究语言模型损失与参数、数据及计算规模之间的幂律关系 边界：经验拟合受研究区间、数据分布和训练设置限制

**P048**　Hoffmann, Jordan; Borgeaud, Sebastian; Mensch, Arthur 等（2022）。[Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)。arXiv:2203.15556。主题：数据与训练计算。

阅读要点：固定训练预算下模型规模和训练 token 应共同配置，展示更充分训练的小模型的价值 边界：不能把研究配比当作所有数据、架构和推理成本约束下的常数

**P049**　Fedus, William; Zoph, Barret; Shazeer, Noam（2021）。[Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity](https://arxiv.org/abs/2101.03961)。arXiv:2101.03961。主题：MoE。

阅读要点：简化稀疏专家路由，并讨论通信与训练稳定性以扩大参数容量 边界：激活计算少不代表存储、通信和部署成本自动少

**P050**　Su, Jianlin; Lu, Yu; Pan, Shengfeng 等（2021）。[RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864)。arXiv:2104.09864。主题：位置编码。

阅读要点：用旋转变换把位置信息融入注意力并体现相对位置关系 边界：位置机制本身不能保证任意上下文长度的可靠外推

**P051**　Ainslie, Joshua; Lee-Thorp, James; de Jong, Michiel 等（2023）。[GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints](https://arxiv.org/abs/2305.13245)。arXiv:2305.13245。主题：推理架构。

阅读要点：在多头与多查询注意力之间引入分组查询，改善推理缓存和速度折中 边界：结论依赖测试模型与上训练设置，不是所有模型可无训练切换

**P052**　Ouyang, Long; Wu, Jeff; Jiang, Xu 等（2022）。[Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)。arXiv:2203.02155。主题：SFT与RLHF。

阅读要点：在作者提示分布的人工评测下，用示范和人类反馈改善指令遵循与偏好表现 边界：人类偏好结果不能推出所有知识推理任务的全面领先，模型仍犯错

**P053**　Hu, Edward J.; Shen, Yelong; Wallis, Phillip 等（2021）。[LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)。arXiv:2106.09685。主题：参数高效微调。

阅读要点：冻结基础权重并训练低秩增量，减少可训练参数和优化器状态 边界：不消除基础模型的存储与前向计算；效果取决于任务和秩等设置

**P054**　Dettmers, Tim; Pagnoni, Artidoro; Holtzman, Ari 等（2023）。[QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)。arXiv:2305.14314。主题：量化微调。

阅读要点：通过量化冻结基座与 LoRA 等技术显著降低微调显存，论文展示 65B 模型在单张 48GB GPU 的配置 边界：硬件结果限定论文序列长度等配置；作者也指出聊天基准可信度问题

**P055**　Rafailov, Rafael; Sharma, Archit; Mitchell, Eric 等（2023）。[Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290)。arXiv:2305.18290。主题：偏好优化。

阅读要点：由特定偏好目标推导直接优化方式，省去典型 RLHF 的显式奖励模型和在线 RL 阶段 边界：依赖偏好数据与参考模型，不保证所有任务优于在线 RL

**P056**　Schulman, John; Wolski, Filip; Dhariwal, Prafulla 等（2017）。[Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)。arXiv:1707.06347。主题：强化学习。

阅读要点：用限制策略变化的代理目标进行多轮小批量策略优化 边界：原论文重点控制与游戏；不能把其结果当作语言模型业务收益

**P057**　Stiennon, Nisan; Ouyang, Long; Wu, Jeff 等（2020）。[Learning to summarize from human feedback](https://arxiv.org/abs/2009.01325)。arXiv:2009.01325。主题：人类偏好训练。

阅读要点：比较摘要并训练奖励模型，用 RL 优化人类偏好而非仅追求 ROUGE 边界：偏好数据与标注者分布限制泛化，奖励不是摘要质量的无误测量

**P058**　Dao, Tri; Fu, Daniel Y.; Ermon, Stefano 等（2022）。[FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135)。arXiv:2205.14135。主题：注意力算子效率。

阅读要点：通过考虑 GPU 内存层级与分块实现精确注意力，减少数据搬运和中间存储 边界：没有将一般稠密注意力的计算复杂度从平方改为线性

**P059**　Dao, Tri（2023）。[FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning](https://arxiv.org/abs/2307.08691)。arXiv:2307.08691。主题：注意力算子效率。

阅读要点：改善 GPU 线程块和 warp 的工作划分，提高硬件利用率 边界：性能数字依赖 A100 等论文硬件与模型设置，不能直接迁移至任意设备

**P060**　Kwon, Woosuk; Li, Zhuohan; Zhuang, Siyuan 等（2023）。[Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180)。arXiv:2309.06180。主题：推理服务与KV管理。

阅读要点：PagedAttention 用分页思想减少 KV cache 碎片并支持共享，提高服务吞吐 边界：收益随模型、序列和并发而变，不能只凭论文倍率作容量承诺

**P061**　Leviathan, Yaniv; Kalman, Matan; Matias, Yossi（2022）。[Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192)。arXiv:2211.17192。主题：推理加速。

阅读要点：草稿模型提出 token、目标模型验证的严格采样算法可保持目标分布并减少串行开销 边界：依赖草稿接受率和系统配置，普通两模型改写不具备分布等价保证

**P062**　Frantar, Elias; Ashkboos, Saleh; Hoefler, Torsten 等（2022）。[GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers](https://arxiv.org/abs/2210.17323)。arXiv:2210.17323。主题：量化。

阅读要点：用近似二阶信息进行高效低比特权重量化 边界：精度和速度受模型、位宽、校准数据、kernel 与硬件限制

**P063**　Lin, Ji; Tang, Jiaming; Tang, Haotian 等（2023）。[AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration](https://arxiv.org/abs/2306.00978)。arXiv:2306.00978。主题：量化。

阅读要点：依据激活统计识别重要通道并设计权重量化策略 边界：原文效果是其模型与部署配置实验，不能泛化为所有 4-bit 方案效果

**P064**　Dettmers, Tim; Lewis, Mike; Belkada, Younes 等（2022）。[LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale](https://arxiv.org/abs/2208.07339)。arXiv:2208.07339。主题：量化。

阅读要点：通过向量量化与异常值的混合精度处理实现大模型 Int8 计算 边界：异常值、数据类型与硬件实现需要验证，低精度不自动等于低延迟

**P065**　Hinton, Geoffrey; Vinyals, Oriol; Dean, Jeff（2015）。[Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531)。arXiv:1503.02531。主题：知识蒸馏。

阅读要点：让学生学习教师或集成模型软目标以形成较易部署的模型 边界：知识转移受学生容量、任务分布与教师错误限制

**P066**　Holtzman, Ari; Buys, Jan; Du, Li 等（2019）。[The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751)。arXiv:1904.09751。主题：采样与解码。

阅读要点：分析开放式文本退化并提出核采样，兼顾多样性与截断不可靠尾部 边界：采样改善生成风格不保证事实正确

**P067**　Lewis, Patrick; Perez, Ethan; Piktus, Aleksandra 等（2020）。[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)。arXiv:2005.11401。主题：RAG。

阅读要点：将参数化序列生成器与外部稠密文档索引结合，在知识密集型任务中评估 边界：原始联合微调结构不同于今天所有检索加生成工程；检索和证据使用仍可失败

**P068**　Karpukhin, Vladimir; Oğuz, Barlas; Min, Sewon 等（2020）。[Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906)。arXiv:2004.04906。主题：稠密检索。

阅读要点：双编码器学习查询与文档表示，在开放域问答中改善候选段落检索 边界：开放域问答结果不能证明任意企业语料都优于关键词检索

**P069**　Guu, Kelvin; Lee, Kenton; Tung, Zora 等（2020）。[REALM: Retrieval-Augmented Language Model Pre-Training](https://arxiv.org/abs/2002.08909)。arXiv:2002.08909。主题：检索预训练。

阅读要点：将知识检索器引入语言模型预训练并在开放域问答验证 边界：训练层方案不等于无需训练的应用 RAG；索引与训练有成本

**P070**　Gao, Luyu; Ma, Xueguang; Lin, Jimmy 等（2022）。[Precise Zero-Shot Dense Retrieval without Relevance Labels](https://arxiv.org/abs/2212.10496)。arXiv:2212.10496。主题：查询与检索增强。

阅读要点：先生成假设文档再检索真实文档，改善无相关性标注时的检索 边界：假设文档可能含虚假细节，不得作为最终事实证据

**P071**　Dosovitskiy, Alexey; Beyer, Lucas; Kolesnikov, Alexander 等（2020）。[An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929)。arXiv:2010.11929。主题：视觉Transformer。

阅读要点：把图像块序列输入 Transformer，在大规模预训练下进行图像识别 边界：原论文是识别任务，不能直接证明视觉语言问答的可靠性

**P072**　Willard, Brandon T.; Louf, Rémi（2023）。[Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702)。arXiv:2307.09702。主题：结构化输出。

阅读要点：通过状态机和文法约束引导语言模型生成可靠格式 边界：保证结构并不保证字段语义和业务事实正确

**P073**　Greshake, Kai; Abdelnabi, Sahar; Mishra, Shailesh 等（2023）。[Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173)。arXiv:2302.12173。主题：工具与RAG安全。

阅读要点：展示将恶意指令嵌入待检索资料的间接提示注入并分析应用风险 边界：具体系统实验不代表所有防御均失败，但仅提示隔离不足以证明安全

## 应用实证与评测

**P074**　Erik Brynjolfsson; Danielle Li; Lindsey Raymond（2025）。[Generative AI at Work](https://doi.org/10.1093/qje/qjae044)。DOI:10.1093/qje/qjae044。主题：真实业务/客服生产率。

阅读要点：5172名客服分批获得辅助工具，平均每小时解决问题数提高15%，收益在人群间不均。 边界：单企业分批部署的准实验，不是全自动客服，也不能推出就业或工资长期变化。

访问补充：[作者托管正式版](https://danielle.li/assets/docs/GenerativeAIatWork.pdf)。出版平台可能限制自动访问；DOI已用Crossref元数据交叉核验。

**P075**　Peng, Sida; Kalliamvakou, Eirini; Cihon, Peter 等（2023）。[The Impact of AI on Developer Productivity: Evidence from GitHub Copilot](https://arxiv.org/abs/2302.06590)。arXiv:2302.06590。主题：业务实证/代码助手。

阅读要点：受控实验中用 Copilot 编写指定 JavaScript HTTP 服务更快。 边界：单一任务与当时产品，不能代表长期维护。

**P076**　Becker, Joel; Rush, Nate; Barnes, Elizabeth 等（2025）。[Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://arxiv.org/abs/2507.09089)。arXiv:2507.09089。主题：业务实证/代码助手。

阅读要点：16位熟悉仓库的开源开发者246项任务，2025年工具组耗时增加19%。 边界：特定开发者与任务；2026更新说明后续实验有选择偏差。

**P077**　Edge, Darren; Trinh, Ha; Cheng, Newman 等（2024）。[From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/abs/2404.16130)。arXiv:2404.16130。主题：企业搜索/GraphRAG。

阅读要点：图社区摘要支持对整库的全局综合问题。 边界：两个约百万token语料、LLM评审；不证明所有检索更优或事实零错误。

**P078**　Jimenez, Carlos E.; Yang, John; Wettig, Alexander 等（2023）。[SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770)。arXiv:2310.06770。主题：代码评测。

阅读要点：用真实GitHub问题、仓库与测试衡量补丁解决率。 边界：测试覆盖不等于完整业务正确性；版本子集和环境会改变结果。

**P079**　Auer, Christoph; Lysak, Maksym; Nassar, Ahmed 等（2024）。[Docling Technical Report](https://arxiv.org/abs/2408.09869)。arXiv:2408.09869。主题：文档解析。

阅读要点：版面分析、表格结构识别与阅读顺序恢复组成解析流水线。 边界：技术报告与自述；未提供目标企业文档集上的独立效果。

**P080**　Thakur, Nandan; Reimers, Nils; Rücklé, Andreas 等（2021）。[BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663)。arXiv:2104.08663。主题：检索评测。

阅读要点：跨领域检索需要异质数据集，BM25是强基线。 边界：原论文数据与模型是历史配置，不能推出2026所有向量模型均不如BM25。

**P081**　Es, Shahul; James, Jithin; Espinosa-Anke, Luis 等（2023）。[Ragas: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217)。arXiv:2309.15217。主题：RAG评测。

阅读要点：分开衡量上下文与回答，提出无参考RAG评估。 边界：模型评审仍依赖评审器能力，不能替代人工真值。

**P082**　Saad-Falcon, Jon; Khattab, Omar; Potts, Christopher 等（2023）。[ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems](https://arxiv.org/abs/2311.09476)。arXiv:2311.09476。主题：RAG评测。

阅读要点：用合成数据训练轻量评审并用人工标注校准统计估计。 边界：领域迁移效果需要复核，不是零人工成本。

**P083**　Gao, Tianyu; Yen, Howard; Yu, Jiatong 等（2023）。[Enabling Large Language Models to Generate Text with Citations](https://arxiv.org/abs/2305.14627)。arXiv:2305.14627。主题：引用与事实评测。

阅读要点：回答正确性、引用支持度和引用覆盖度需分别评估。 边界：引用文字与原始事实的真实性是不同层面。

**P084**　Min, Sewon; Krishna, Kalpesh; Lyu, Xinxi 等（2023）。[FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation](https://arxiv.org/abs/2305.14251)。arXiv:2305.14251。主题：事实评测。

阅读要点：将长文拆成原子事实检查支持比例。 边界：精确率高不代表完整，拆分和检索本身也可能出错。

**P085**　Zheng, Lianmin; Chiang, Wei-Lin; Sheng, Ying 等（2023）。[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)。arXiv:2306.05685。主题：LLM评审。

阅读要点：评审模型可近似人类偏好，但存在位置、冗长和自我偏好。 边界：人类一致度只在原文任务与协议成立。

**P086**　Jain, Naman; Han, King; Gu, Alex 等（2024）。[LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code](https://arxiv.org/abs/2403.07974)。arXiv:2403.07974。主题：代码评测/污染。

阅读要点：按题目发布时间动态评测降低污染风险，涵盖修复/执行/输出预测。 边界：发布日期晚于已知截止不能保证训练来源绝无重叠。

**P087**　Ghosh, Dhruba; Hajishirzi, Hanna; Schmidt, Ludwig（2023）。[GenEval: An Object-Focused Framework for Evaluating Text-to-Image Alignment](https://arxiv.org/abs/2310.11513)。arXiv:2310.11513。主题：图像评测。

阅读要点：检测对象、颜色、数量、位置以诊断组合遵循。 边界：自动检测器会误判，覆盖面有限。

**P088**　Heusel, Martin; Ramsauer, Hubert; Unterthiner, Thomas 等（2017）。[GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium](https://arxiv.org/abs/1706.08500)。arXiv:1706.08500。主题：图像指标。

阅读要点：提出FID比较真实和生成图像特征分布。 边界：分布指标不衡量单图文字要求或业务可用率。

**P089**　Hessel, Jack; Holtzman, Ari; Forbes, Maxwell 等（2021）。[CLIPScore: A Reference-free Evaluation Metric for Image Captioning](https://arxiv.org/abs/2104.08718)。arXiv:2104.08718。主题：多模态指标。

阅读要点：CLIP图文表示可衡量图像描述兼容性。 边界：原任务是图像描述评价；不是生成图像细节正确性的保证。

**P090**　Huang, Ziqi; He, Yinan; Yu, Jiashuo 等（2023）。[VBench: Comprehensive Benchmark Suite for Video Generative Models](https://arxiv.org/abs/2311.17982)。arXiv:2311.17982。主题：视频评测。

阅读要点：把视频质量拆成16个可解释维度并用人类偏好校验。 边界：旧版套件不足以覆盖全部物理因果或专业创作要求。

**P091**　Unterthiner, Thomas; van Steenkiste, Sjoerd; Kurach, Karol 等（2018）。[Towards Accurate Generative Models of Video: A New Metric & Challenges](https://arxiv.org/abs/1812.01717)。arXiv:1812.01717。主题：视频指标。

阅读要点：FVD用视频特征比较生成分布并考虑时间信息。 边界：受特征模型和样本配置影响，不等于长程物理真实性。

**P092**　Kilgour, Kevin; Zuluaga, Mauricio; Roblek, Dominik 等（2018）。[Fréchet Audio Distance: A Metric for Evaluating Music Enhancement Algorithms](https://arxiv.org/abs/1812.08466)。arXiv:1812.08466。主题：音频指标。

阅读要点：FAD比较音频特征分布，在音乐增强中验证感知相关性。 边界：最初音乐增强验证不等于所有语音和音乐任务有效。

**P093**　Du, Zhihao; Wang, Yuxuan; Chen, Qian 等（2024）。[CosyVoice 2: Scalable Streaming Speech Synthesis with Large Language Models](https://arxiv.org/abs/2412.10117)。arXiv:2412.10117。主题：语音生成。

阅读要点：语言模型和分块flow matching支持流式/非流式语音合成。 边界：作者自然度宣传与指定实验不同于所有业务；流式延迟依硬件。

**P094**　Zhou, Shuyan; Xu, Frank F.; Zhu, Hao 等（2023）。[WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854)。arXiv:2307.13854。主题：浏览器Agent评测。

阅读要点：可复现网站与功能性任务成功判据。 边界：仿真环境与真实业务账号、权限、网络均有差异。

**P095**　Xie, Tianbao; Zhang, Danyang; Chen, Jixuan 等（2024）。[OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972)。arXiv:2404.07972。主题：计算机Agent评测。

阅读要点：真实桌面环境和执行脚本测试跨应用终态。 边界：历史369任务并不覆盖所有长程业务；环境变化影响复现。

**P096**　Yuan, Mengqi; Zhou, Zilong; Xiong, Xinzhuang 等（2026）。[OSWorld 2.0: Benchmarking Computer Use Agents on Long-Horizon Real-World Tasks](https://arxiv.org/abs/2606.29537v2)。arXiv:2606.29537。主题：长程Agent评测。

阅读要点：v2摘要报告108个长程工作流；500步上限下Claude Opus 4.8、maximum thinking与批量工具调用的最优配置整任务完成率20.6%、部分得分54.8%。 边界：预印本；特定500步预算，整任务与部分得分不可混用。

**P097**　Liang, Percy; Bommasani, Rishi; Lee, Tony 等（2022）。[Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110)。arXiv:2211.09110。主题：模型综合评测。

阅读要点：在共同任务协议下联合评准确性、校准、鲁棒性、公平性、偏见、毒性和效率。 边界：任何覆盖都是有限选择，不能压成普适单一分数。

**P098**　Liu, Yang; Iter, Dan; Xu, Yichong 等（2023）。[G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634)。arXiv:2303.16634。主题：LLM评审。

阅读要点：把评价标准转为结构化评审提高部分文本任务上的人类相关性。 边界：原研究也提醒LLM生成文本偏好，指标跨任务需重新校准。

## 官方文档 工程材料 开源项目与课程

这些资料不计入论文数量。仓库是实现与复现入口，官方博客是项目方经验陈述；两者均不能单独证明普遍业务效果。

- **S001** [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)。一手工程博客。直接阅读全文可见文本，使用其工作流/Agent区分、简单可组合模式和绝对路径工具案例；为作者实践而非独立RCT。

- **S002** [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)。一手工程博客。直接阅读正文，使用即时加载、压缩、结构化笔记与上下文资源管理经验；未将生物工作记忆类比当机制证明。

- **S003** [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)。一手工程复盘。直接阅读正文，4倍/15倍为作者自身数据下相对聊天的token使用，非通用倍数；分工、可恢复执行和trace经验。

- **S004** [Wan2.1 official repository](https://github.com/Wan-Video/Wan2.1)。官方开源仓库。读取README，T2V-1.3B/RTX4090/5秒480P/约4分钟为作者配置声明，8.19GB非全配置需求。

- **S005** [s1 official repository](https://github.com/simplescaling/s1)。官方开源仓库。读取README核对模型/训练/评测资源；视频入口未观看，未声称有视频证据。

- **S006** [Stanford CS336: Language Modeling from Scratch (Spring 2025)](https://cs336.stanford.edu/spring2025/index.html)。课程官网与材料索引。已读取课程官网、教师信息与大纲；未逐讲观看课程视频。作者 Tatsunori Hashimoto、Percy Liang。

- **S007** [Let's build GPT: from scratch, in code, spelled out.](https://www.youtube.com/watch?v=kCc8FmEb1nY)。作者原始视频。核验原始 YouTube 页面标题、作者 Andrej Karpathy；下载原始 HTML 并定位公开视频说明中的 00:09:28、00:22:11、01:02:00、01:48:53 章节文本。未逐帧观看。

- **S008** [How caching works — Hugging Face Transformers](https://huggingface.co/docs/transformers/main/cache_explanation)。官方文档。读取 KV cache 原理、因果注意力、缓存张量布局与生成循环说明。访问 main 文档，具体 API 不作固定版本保证。

- **S009** [Structured Outputs — vLLM v0.31.0](https://docs.vllm.ai/en/v0.31.0/features/structured_outputs/)。开源项目官方文档。读取官方检索结果对 JSON schema、文法约束及 structured_outputs 的说明；正文仅用于机制与能力说明，不提供未验证的 SDK 代码。

- **S010** [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents)。厂商工程实践。读取原始页面检索内容中的原型、评测、保留测试集、无效参数、重复调用、token 消耗与工具响应建议。发布 2025-09-11。视为厂商自身实践，不外推普遍增益。

- **S011** [Dive into Deep Learning：Word Embedding (word2vec)](https://d2l.ai/chapter_natural-language-processing-pretraining/word2vec.html)。官方开放教材。读取词向量/skip-gram 原理与 Figure 15.1.1；核验固定提交 LICENSE-SUMMARY，教材插图 CC BY-SA 4.0，不混用示例代码许可。

- **S012** [Dive into Deep Learning：Queries, Keys, and Values](https://d2l.ai/chapter_attention-mechanisms-and-transformers/queries-keys-values.html)。官方开放教材。读取 QKV 与 Figure 11.1.1；使用 qkv.svg，核验图号与文档许可。

- **S013** [Dive into Deep Learning：The Transformer Architecture](https://d2l.ai/chapter_attention-mechanisms-and-transformers/transformer.html)。官方开放教材。读取 Figure 11.7.1 与编码器解码器结构解释；原图按白底 SVG 转 PNG，未修改内容。

- **S014** [CompVis：Latent Diffusion 官方仓库](https://github.com/CompVis/latent-diffusion)。官方开源仓库。核验官方 modelfigure.png 与论文 Figure 3 对应；采用固定提交资产与 MIT 许可，保留原图分辨率、完整版权和许可。

- **S015** [vLLM：Hybrid KV Cache Manager](https://docs.vllm.ai/en/latest/design/hybrid_kv_cache_manager/)。官方工程设计文档。读取 Memory Layout 对 10 全注意力层/20 滑动窗口层示例说明及文档版本警告；核验固定提交图片与 Apache-2.0 许可。

- **S016** [GraphRAG Documentation](https://microsoft.github.io/graphrag/)。official documentation。读取官方项目文档入口与能力说明；用于解释检索路径、索引成本和工程配置，不作独立业务收益证据。

- **S017** [GraphRAG official repository and maintenance notice](https://github.com/microsoft/graphrag)。official open-source repository。读取README索引成本、提示调整、研究示范非正式支持产品及主要进入维护模式说明。

- **S018** [Docling — Get your documents ready for gen AI](https://github.com/docling-project/docling)。official open-source repository。读取README特性、结构化文档、OCR/VLM与接口；未自行运行。

- **S019** [Dify](https://github.com/langgenius/dify)。official open-source repository。读取README关于workflow、RAG、观测和API；未将星标和功能声明解释为生产效果。

- **S020** [ComfyUI](https://github.com/Comfy-Org/ComfyUI)。official open-source repository。读取节点图、图像视频音频工作流、JSON保存与API说明；未采纳最快等营销措辞为已验证事实。

- **S021** [Whisper model card](https://github.com/openai/whisper/blob/main/model-card.md)。official model card。读取局限与性能差异说明；支持对幻觉、语言和口音差异的讨论。

- **S022** [CosyVoice](https://github.com/QwenAudio/CosyVoice)。official open-source repository。由旧FunAudioLLM地址重定向；读取训练推理部署README；未试听全部样例或测量实时性能。

- **S023** [We are Changing our Developer Productivity Experiment Design](https://metr.org/blog/2026-02-24-uplift-update/)。official research update。读取全文关键研究方法与局限；后续研究因参与者与任务选择、并行计时问题难以可靠估计当时效应。

- **S024** [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)。official engineering blog。读取任务、试次、轨迹、评分器分类及上线评估建议；标注供应商与客户经验，非独立RCT。

- **S025** [Q: What’s a minimum viable evaluation setup? — Hamel Husain and Shreya Shankar](https://hamel.dev/blog/posts/evals-faq/whats-a-minimum-viable-evaluation-setup.html)。first-person practitioner blog。读取作者关于少量真实轨迹、领域专家与错误分析的建议；不是最低统计样本量证明。

- **S026** [LLMOps — Josh Tobin, Full Stack Deep Learning / The Full Stack (2023-05-09)](https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/llmops/)。official video lecture chapter summaries。依据官方章节摘要；页面包含视频入口；未完整观看视频或核验逐句字幕，因此不提供未经核验时间点。历史模型推荐不作2026选型依据。

- **S027** [BEIR official repository](https://github.com/beir-cellar/beir)。official open-source repository。用于交叉核验检索评测项目及数据集入口。

- **S028** [ARES official repository](https://github.com/stanford-futuredata/ARES)。official open-source repository。读取自动评审、人工校准与prediction-powered inference概述；不重复计入论文。

- **S029** [LiveCodeBench official repository](https://github.com/LiveCodeBench/LiveCodeBench)。official open-source repository。读取时间窗口、release版本及lite默认测试配置差异。

- **S030** [VBench official repository](https://github.com/Vchitect/VBench)。official open-source repository。读取分维度评测与标准提示套件说明；不同版本不混用成绩。

- **S031** [SWE-agent official repository and mini-swe-agent transition notice](https://github.com/SWE-agent/SWE-agent)。official open-source repository。读取README维护方向与建议新用户使用mini-swe-agent的提示；未把项目同等性能自述当独立复现结论。

- **S032** [Docling Document concepts](https://docling-project.github.io/docling/concepts/docling_document/)。官方文档。实际读取统一DoclingDocument对象、层级、表格、布局与provenance说明；用于区分原生文档对象和教学Invoice业务对象。

- **S033** [Docling Architecture](https://docling-project.github.io/docling/concepts/architecture/)。官方文档与仓库图片。核验官方架构图在MIT仓库固定提交中的文件；图片已本地查看。

- **S034** [SWE-agent Architecture](https://swe-agent.com/latest/background/architecture/)。官方文档与仓库图片。实际读取工程架构文档并核验MIT仓库架构图；图反映所引文档实现，不混作2024论文配置。

- **S035** [ComfyUI Text to Image Workflow](https://docs.comfy.org/tutorials/basic/text-to-image)。官方教程与仓库图片。实际读取节点解释并查看官方A–F工作流图。仅归纳节点数据流，不采用其最佳入门模型或性能宣传；图片取GPLv3 docs仓库固定提交，原图和完整许可保存。

- **S036** [Attention in transformers, step-by-step | Deep Learning Chapter 6](https://www.3blue1brown.com/lessons/attention/)。官方视频文字改编。读取官方图解文字；作者 Grant Sanderson，文字改编 Justin Sun；未宣称完整观看视频，不提供未核验时间点。

- **S037** [Stanford CS336 Spring 2025 Lecture 1 Overview and Tokenization](https://www.youtube.com/watch?v=SQ3fZ1sAqXI)。官方课程视频。Stanford Online标题和简介，配合官方课程表；未获取可核验分钟时间点的字幕。

- **S038** [Project Walkthrough askFSDL — Charles Frye, 2023-05-09](https://fullstackdeeplearning.com/llm-bootcamp/spring-2023/askfsdl-walkthrough/)。公开项目实践及视频官方摘要。读取数据清洗、ETL、检索、监测等章节摘要；视频pUKs4xM1r5U；无量化效果数据。

- **S039** [Hugging Face LLM Course](https://huggingface.co/learn/llm-course/en/chapter1/1)。官方课程。读取课程简介和目录，核验涉及Transformers、Datasets、Tokenizers和微调。

- **S040** [Dive into Deep Learning](https://d2l.ai/)。作者官方教材。教材首页与Attention/Transformer目录，用于基础数学与深度学习阅读建议。

- **S041** [Stripe Idempotent requests](https://docs.stripe.com/api/idempotent_requests)。官方API文档。核验重试时复用幂等键、参数一致性与保留期说明；本文提炼逻辑动作作用域，不移植所有Stripe语义。


## 按任务查找项目与实现入口

该索引对应正文案例与机制，不表示所有项目已经由本次调研运行或压测。对照正文的适用边界选择一个入口，固定版本后再做实验；仓库默认分支、文档和依赖可能继续变化。

| 任务或学习目的 | 项目入口 | 先阅读什么 | 优先如何评测 |
|---|---|---|---|
| 全库主题总结与关系探索 | [Microsoft GraphRAG](https://microsoft.github.io/graphrag/) | 索引与查询；官方仓库已说明维护模式，采用前核对支持范围 | 全局与事实查询分开；覆盖面、证据支持、索引成本 |
| 可视化业务流程与模型接入 | [Dify](https://github.com/langgenius/dify) | Workflow、知识库、API、运行日志 | 节点契约与整链成功分别测；权限及回归 |
| 文档结构恢复与RAG输入 | [Docling](https://github.com/docling-project/docling) | 文档对象、OCR、布局、表格与导出 | 字段、阅读顺序、单位、页码回链和下游问答 |
| 仓库级代码修复 | [SWE-agent](https://github.com/SWE-agent/SWE-agent) / [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent/) | 历史论文研究接口设计；当前仓库推荐后者作为较简单入口 | 修复测试、回归测试、补丁范围和预算 |
| 浏览器与桌面任务评测 | [WebArena](https://webarena.dev/) / [OSWorld](https://os-world.github.io/) | 环境重置、任务定义、终态校验 | 完成率、部分分、步骤数、过程违规和重复可靠性 |
| 图像视频素材流程 | [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | 节点图、工作流保存与API | 多种子可用率、内容约束、人工挑选与重跑成本 |
| 开放视频生成实现 | [Wan2.1](https://github.com/Wan-Video/Wan2.1) | 模型配置、生成任务、显存与示例条件 | 时间一致性、指令遵循、生成耗时与实际素材验收 |
| 音频识别与输出 | [Whisper](https://github.com/openai/whisper) / [CosyVoice](https://github.com/QwenAudio/CosyVoice) | 模型卡、任务边界、流式推理说明 | WER/CER及关键术语、自然度、首包延迟与打断 |
| 理解高效推理服务 | [vLLM](https://github.com/vllm-project/vllm) | 分页KV缓存、调度、版本对应的功能文档 | 真实长度与并发分布下TTFT、TPOT、吞吐和质量 |

同一个项目可以用于多个阶段。例如 Docling 是 RAG 的数据入口，GraphRAG 是索引与回答的一种组合，Dify 是编排平台，vLLM 是推理服务，它们不处于同一抽象层。不要因为都带有 AI 标签就把它们当作可互换产品，也不要为学习一次把所有框架装进同一系统。
