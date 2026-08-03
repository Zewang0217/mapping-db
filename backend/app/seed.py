"""Seed the dimension_values table with 26 canonical values on first run."""

from app.database import get_pool

DIMENSION_VALUES = [
    # Source (5 values)
    ("source", "供应链", "恶意来自第三方依赖、仓库、包管理器的构建/分发环节"),
    ("source", "用户输入", "恶意指令直接来自用户写的 prompt、对话、上传的文件"),
    ("source", "外部不可信内容", "恶意藏在 URL、网页、引用的外部数据中"),
    ("source", "运行时环境", "恶意来自 MCP server、其他 agent、系统进程"),
    ("source", "来源不明", "原始分类未陈述攻击从哪个渠道进入"),

    # Mechanism (values used so far; 按需增长 — unencountered values are NOT pre-seeded)
    ("mech", "指令操纵", "以自然语言/文本为载体，作用于模型的理解与决策层，使模型做出本不会做的选择或输出"),
    ("mech", "混淆隐藏", "可叠加属性（不参与主值互斥判定）：通过隐藏/混淆规避检测"),
    ("mech", "状态污染", "污染持久状态——记忆投毒、自修改、持久化后门、跨会话污染"),
    ("mech", "方式不明", "原始分类未陈述具体攻击手段"),
    # 暂不预置（未遇到）：代码执行、依赖操纵、权限滥用 — 映射中遇到再讨论加回

    # Target (values used so far)
    ("target", "窃取信息", "违反机密性——读取/外传敏感数据、环境变量、系统提示"),
    ("target", "破坏系统", "违反完整性和可用性——加密勒索、删除数据、植入后门"),
    ("target", "持久控制", "违反控制性——写 cron、改配置、创建进程驻留"),
    ("target", "绕过防御", "反检测、反拒绝、混淆意图以逃避安全策略"),
    ("target", "资源滥用", "间接违反可用性——盗用计算资源、API quota 挖矿"),
    ("target", "内容安全危害", "违反内容安全——模型输出可致物理伤害/违法/自残等有害内容，受害对象是工具用户（人）"),
    ("target", "目标不明", "原始分类未陈述攻击的最终后果"),

    # Vulnerability tags (8 values, 2026-08-02 literature-grounded revision)
    ("vuln", "缺乏输入验证与信任隔离", "系统未验证输入来源和可信度就纳入执行上下文；未区分指令与数据（数据-指令边界缺失）"),
    ("vuln", "供应链完整性缺失", "依赖版本未固定、未验证来源完整性与出处（原：依赖未锁定）"),
    ("vuln", "权限过宽（最小权限违反）", "工具授权范围远超实际需要，违反最小权限原则（原：权限过宽（通配符））"),
    ("vuln", "缺乏输出过滤", "未对模型/工具输出做安全过滤和消毒"),
    ("vuln", "状态未隔离", "用户或会话间的状态未隔离导致交叉污染"),
    ("vuln", "未声明能力与实际不符", "skill 声明的功能与实际行为不一致（Unit 42 BIV）"),
    ("vuln", "敏感信息泄露", "系统未保护可访问的敏感数据——凭据、PII、系统提示、上下文（OWASP LLM02/LLM07）"),
    ("vuln", "过度自主/缺人机确认", "高影响操作无人工确认门，单次批准后长期有效（OWASP LLM06）"),

    # Carrier tags (through which medium the attack operates; like vuln tags, optional)
    ("carrier", "提示词", "攻击经文本/指令载体实施——注入、覆盖、越狱指令"),
    ("carrier", "代码", "攻击经代码载体实施——脚本、程序逻辑"),
    ("carrier", "网络", "攻击经网络载体实施——数据外传、远程请求"),
    ("carrier", "文件", "攻击经文件系统载体实施——枚举、读取、写入敏感文件"),
    ("carrier", "数据", "攻击经数据载体实施——环境变量、配置、上下文中的敏感数据"),
    ("carrier", "状态", "攻击经状态载体实施——记忆、会话、持久状态"),
    ("carrier", "依赖", "攻击经依赖载体实施——包、库、外部组件"),
    ("carrier", "权限", "攻击经权限载体实施——授权范围、通配符、提权"),
    ("carrier", "载体不明", "原始分类未陈述攻击通过的媒介"),
]


async def seed_dimension_values():
    """Insert canonical dimension values if the table is empty."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchval("SELECT COUNT(*) FROM dimension_values")
        if existing > 0:
            return  # already seeded

        for dim, name, definition in DIMENSION_VALUES:
            await conn.execute(
                "INSERT INTO dimension_values (dimension, value_name, definition) "
                "VALUES ($1, $2, $3) ON CONFLICT (dimension, value_name) DO NOTHING",
                dim, name, definition,
            )
