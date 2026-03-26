# ToolArch — References

> 持续更新的参考文献库。论文、竞品、开源项目、技术博客。
> 每条标注：关联模块 + 对我们的启发/警示 + 状态（待读/已读/已应用）

---

## 📄 论文

### 代码分析 & 架构

| 论文 | 关键发现 | 关联模块 | 对 ToolArch 的影响 | 状态 |
|------|---------|---------|-------------------|------|
| [The Evolution of Tool Use in LLM Agents](https://arxiv.org/abs/2603.22862) (2026-03) | 工具使用从单调用→多工具编排的演进 | MCP Server (V1) | Agent 如何消费 ToolArch 的 MCP 工具 | ⏳ 待读 |
| [AI-Generated Code Is Not Reproducible (Yet)](https://arxiv.org/abs/2512.22387) (2025-12) | LLM 生成代码的依赖缺口，可复现性差 | 分析器 | AI 生成代码的架构质量是 ToolArch 的核心场景 | ⏳ 待读 |

### 代码理解 & Graph

| 论文 | 关键发现 | 关联模块 | 对 ToolArch 的影响 | 状态 |
|------|---------|---------|-------------------|------|
| [ToolRosetta](https://arxiv.org/abs/2603.XXXXX) (2026-03) | 通过自动化工具标准化桥接开源仓库和 LLM Agent | Graph Adapter | 工具标准化思路可参考 adapter 接口设计 | ⏳ 待读 |

### 软件架构指标（经典）

| 论文/书 | 关键内容 | 关联模块 | 对 ToolArch 的影响 | 状态 |
|---------|---------|---------|-------------------|------|
| Robert C. Martin — Agile Software Development (2002) | 稳定性(I)、抽象性(A)、主序列距离(D) | Martin Metrics | 核心指标体系的理论来源 | ✅ 已应用 |
| Tarjan — Depth-First Search and Linear Graph Algorithms (1972) | 强连通分量算法 → 循环依赖检测 | Cycle Detection | 核心算法 | ✅ 已应用 |
| McCabe — A Complexity Measure (1976) | 圈复杂度 | Complexity Analyzer | 函数/模块复杂度评估 | ✅ 已应用 |
| Chidamber & Kemerer — Metrics Suite for OOD (1994) | CBO/WMC/DIT/RFC/LCOM 面向对象指标 | OO Metrics (V2) | Java 分析时可加入 CK 指标集 | ⏳ 待用 |

---

## 🔧 开源项目 — 竞品/参考

### Layer 1 竞品（代码上下文引擎）— 我们不重造，但要深度了解

| 项目 | Stars | 技术栈 | 核心能力 | 和 ToolArch 的关系 | 监控频率 |
|------|-------|--------|---------|-------------------|---------|
| [GitNexus](https://github.com/abhigyanpatwari/GitNexus) | 18.2K | Tree-sitter + KuzuDB WASM | 零服务器代码智能, 13 语言, Graph RAG, blast radius | 潜在上游（Graph Adapter 数据源） | **周度** |
| [code-review-graph](https://github.com/tirth8205/code-review-graph) | 3.5K | Tree-sitter + SQLite | Claude Code 专用, 49x token 节省, blast radius | 潜在上游（轻量 adapter 候选） | **周度** |
| [code-graph-rag](https://github.com/vitali87/code-graph-rag) | 1.7K | Tree-sitter + Memgraph | 11 语言, 语义搜索(UniXcoder), MCP server | 参考实现 | 月度 |
| [CodePrism](https://github.com/rustic-ai/codeprism) | ~1K | Rust + 自定义内存图 | 1000+ files/sec, 20 MCP 工具, 100% AI 生成 | 性能标杆参考 | 月度 |

### Layer 2 参考（架构分析工具）

| 项目 | Stars | 定位 | 参考价值 | 状态 |
|------|-------|------|---------|------|
| [ArchGuard](https://github.com/archguard/archguard) | ~2K | Thoughtworks 架构治理平台 | 指标体系 + 规则引擎设计 | 已分析 |
| [SonarQube](https://github.com/SonarSource/sonarqube) | ~9K | 代码质量平台 | 规则引擎 + 报告模板，但不做架构级分析 | 了解 |
| [CodeScene](https://codescene.com/) | 商业 | 行为代码分析 | 社会复杂度概念有趣，但方向不同 | 了解 |
| [jQAssistant](https://github.com/jQAssistant) | ~1K | Java 架构约束验证 | Java 分层合规检查参考 | 待看 |
| [Depends](https://github.com/nicedoc/depends) | ~500 | 多语言依赖提取 | 依赖分析算法参考 | 待看 |
| [pydeps](https://github.com/thebjorn/pydeps) | ~2K | Python 模块依赖可视化 | Python 解析 + 可视化参考（MVP 直接相关） | **待看** |
| [vulture](https://github.com/jendrikseipp/vulture) | ~3K | Python 死代码检测 | 死代码分析器参考 | 待看 |

### 上游依赖

| 项目 | 我们用的 | 监控重点 | 频率 |
|------|---------|---------|------|
| [Tree-sitter](https://github.com/tree-sitter/tree-sitter) | AST 解析 | Python/Java grammar 更新, 新语言支持 | 月度 |
| [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter) | Python bindings | API 变更 | 月度 |
| [tree-sitter-python](https://github.com/tree-sitter/tree-sitter-python) | Python grammar | 3.12/3.13 语法支持 | 月度 |

---

## 📝 技术博客/文章

| 文章 | 来源 | 关键内容 | 对 ToolArch 的影响 |
|------|------|---------|-------------------|
| Apideck CLI vs MCP (2026-03, HN 251pt) | HN/Blog | MCP 3 服务 55K token，CLI 模式更高效 | ToolArch MCP Server (V1) 要精简返回数据 |
| Agentic Engineering Patterns (Simon Willison) | Blog | Coding Agent 如何消费工具 | V1 MCP 接口设计参考 |
| ArchUnit (Java) 架构测试 | Blog | Java 项目架构约束单元测试 | V2 Java 分层合规参考 |

---

## 🎯 上游项目选型（待深度调研）

**目的**：选定一个上游项目作为 Graph Adapter 的首选数据源。

### 评估维度

| 维度 | GitNexus | code-review-graph | 备注 |
|------|----------|-------------------|------|
| Stars | 18.2K | 3.5K | |
| Java 支持深度 | 13 语言含 Java | 多语言含 Java | 需测试泛型/Lambda/注解质量 |
| 本地部署 | 浏览器 WASM（零服务器） | SQLite（极轻量） | code-review-graph 更适合 CLI |
| 扩展机制 | MCP + Claude Code hooks | Claude Code plugin + pip | 需看 API 稳定性 |
| 社区活跃度 | 高（18K stars） | 中（3.5K stars, v1.8.4 活跃） | |
| PR 友好度 | 待确认 | 待确认 | 看 CONTRIBUTING.md |
| 数据输出格式 | KuzuDB (Cypher) | SQLite | ToolArch adapter 需适配 |

**结论**：待 P0 骨架搭完后，实际跑两个项目做深度对比。

---

## ⚠️ 踩坑预警

| 风险 | 来源 | 预防措施 |
|------|------|---------|
| Tree-sitter Python grammar 不支持某些新语法 | 版本滞后 | 定期更新 grammar, 增量测试 |
| SQLite 大仓库图谱查询慢 | 数据量增长 | 加索引 + 分析 EXPLAIN QUERY PLAN |
| 上游项目 breaking change | 开源风险 | Graph Adapter 隔离层是核心防护 |
| Python 动态导入/monkey-patch 无法静态分析 | 语言特性 | 标注为"动态导入，不可静态分析" + 告警 |
| Martin 指标对 Python 的适用性 | Martin 指标为 Java/C++ 设计 | 需要调整：Python 的 package = Java 的 package, module = class |
| AI 生成代码的架构质量特征不同于人写代码 | 新现象 | 这本身可以成为面试话题和研究方向 |

---

## 📅 更新日志

- **2026-03-26**: 初始创建。纳入 3/25 竞品调研（4 个 Layer 1 竞品）+ Pulse 论文 + 经典架构指标文献
- 下次更新：P0 骨架搭完后，上游项目实际跑测对比
